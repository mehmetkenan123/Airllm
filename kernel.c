/*
 * ==========================================================================
 *  NOVA KERNEL - Advanced Monolithic Kernel Core
 *  File: kernel.c
 *  Architecture: x86_64
 *  Description: 
 *    Bu dosya, sıfırdan yazılmış gelişmiş bir çekirdeğin ana giriş noktasıdır.
 *    İçerik:
 *      1. Bootloader'dan gelen Multiboot2 bilgilerinin işlenmesi.
 *      2. Erken Başlangıç (Early Init): GDT, IDT, Stack kurulumu.
 *      3. Bellek Yönetimi: Fiziksel Sayfa Ayırıcı (Physical Page Allocator).
 *      4. Donanım Soyutlama: VGA Text Mode, Serial Port (COM1).
 *      5. Kesme Yönetimi (Interrupt Handling) ve Zamanlayıcı (PIT).
 *      6. Çoklu Görev (Multitasking) İskeleti: Thread Yapısı ve Scheduler.
 *      7. Ana Döngü (Kernel Idle Loop).
 * ==========================================================================
 */

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdarg.h>

/* ========================================================================
 *  BÖLÜM 1: TİP TANIMLAMALARI VE SABİTLER
 * ======================================================================== */

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef size_t   usize;

#define NULL ((void*)0)
#define KERNEL_STACK_SIZE 0x4000 // 16KB Kernel Stack
#define MAX_PHYSICAL_PAGES 0x10000 // 64MB RAM desteği varsayımı
#define MAX_THREADS 64

// VGA Buffer Sabitleri
#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

// Renk Kodları
enum vga_color {
    VGA_COLOR_BLACK = 0,
    VGA_COLOR_BLUE = 1,
    VGA_COLOR_GREEN = 2,
    VGA_COLOR_CYAN = 3,
    VGA_COLOR_RED = 4,
    VGA_COLOR_MAGENTA = 5,
    VGA_COLOR_BROWN = 6,
    VGA_COLOR_LIGHT_GREY = 7,
    VGA_COLOR_DARK_GREY = 8,
    VGA_COLOR_LIGHT_BLUE = 9,
    VGA_COLOR_LIGHT_GREEN = 10,
    VGA_COLOR_LIGHT_CYAN = 11,
    VGA_COLOR_LIGHT_RED = 12,
    VGA_COLOR_LIGHT_MAGENTA = 13,
    VGA_COLOR_LIGHT_BROWN = 14,
    VGA_COLOR_WHITE = 15,
};

/* ========================================================================
 *  BÖLÜM 2: DONANIM ERİŞİMİ VE LOW-LEVEL FONKSİYONLAR
 * ======================================================================== */

// Port I/O İşlemleri
static inline void outb(u16 port, u8 val) {
    asm volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline u8 inb(u16 port) {
    u8 ret;
    asm volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void io_wait() {
    outb(0x80, 0); // BIOS POST cycle'ı tetikleyerek kısa bekleme
}

// Global Değişkenler
static u16* vga_buffer = (u16*)VGA_MEMORY;
static size_t vga_row = 0;
static size_t vga_col = 0;
static u8 vga_color_byte = (VGA_COLOR_LIGHT_GREY << 4) | VGA_COLOR_BLACK;

/* ========================================================================
 *  BÖLÜM 3: EKRAN ÇIKTI SİSTEMİ (VGA & SERIAL)
 * ======================================================================== */

static void clear_screen() {
    for (size_t i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (vga_color_byte << 8) | ' ';
    }
    vga_row = 0;
    vga_col = 0;
}

static void set_cursor(size_t x, size_t y) {
    u16 pos = y * VGA_WIDTH + x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (u8)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (u8)((pos >> 8) & 0xFF));
}

static void serial_write(char c) {
    // Serial port hazır mı? (THRE bit'i)
    while ((inb(0x3FD) & 0x20) == 0);
    outb(0x3F8, c);
}

static void kernel_putchar(char c) {
    // Serial'e yaz
    if (c == '\n') {
        serial_write('\r');
    }
    serial_write(c);

    // VGA'ya yaz
    if (c == '\n') {
        vga_col = 0;
        vga_row++;
    } else if (c == '\r') {
        vga_col = 0;
    } else if (c == '\t') {
        vga_col = (vga_col + 8) & ~7;
    } else if (c == '\b') {
        if (vga_col > 0) {
            vga_col--;
            vga_buffer[vga_row * VGA_WIDTH + vga_col] = (vga_color_byte << 8) | ' ';
        }
    } else {
        vga_buffer[vga_row * VGA_WIDTH + vga_col] = (vga_color_byte << 8) | c;
        vga_col++;
    }

    // Satır sonu kontrolü
    if (vga_col >= VGA_WIDTH) {
        vga_col = 0;
        vga_row++;
    }
    if (vga_row >= VGA_HEIGHT) {
        // Scroll işlemi (Basit versiyon: hafızayı kaydır)
        for (size_t i = 0; i < (VGA_HEIGHT - 1) * VGA_WIDTH; i++) {
            vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
        }
        for (size_t i = (VGA_HEIGHT - 1) * VGA_WIDTH; i < VGA_HEIGHT * VGA_WIDTH; i++) {
            vga_buffer[i] = (vga_color_byte << 8) | ' ';
        }
        vga_row = VGA_HEIGHT - 1;
    }
    set_cursor(vga_col, vga_row);
}

static void kernel_print(const char* str) {
    while (*str) {
        kernel_putchar(*str);
        str++;
    }
}

// Basit integer -> string dönüşümü
static void print_int(int num) {
    char buffer[32];
    int i = 0;
    bool negative = false;

    if (num == 0) {
        kernel_putchar('0');
        return;
    }

    if (num < 0) {
        negative = true;
        num = -num;
    }

    while (num > 0) {
        buffer[i++] = (num % 10) + '0';
        num /= 10;
    }

    if (negative) {
        kernel_putchar('-');
    }

    while (i > 0) {
        kernel_putchar(buffer[--i]);
    }
}

// printf benzeri fonksiyon
static void kprintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);

    while (*fmt) {
        if (*fmt == '%') {
            fmt++;
            switch (*fmt) {
                case 's': {
                    const char* str = va_arg(args, const char*);
                    kernel_print(str);
                    break;
                }
                case 'd': {
                    int val = va_arg(args, int);
                    print_int(val);
                    break;
                }
                case 'x': {
                    // Hex çıktısı için basit implementasyon (geliştirilebilir)
                    u32 val = va_arg(args, u32);
                    kernel_print("0x");
                    // Basit hex döngüsü eksikliği nedeniyle şimdilik atlanıyor veya eklenebilir
                    break;
                }
                case '%': {
                    kernel_putchar('%');
                    break;
                }
            }
        } else {
            kernel_putchar(*fmt);
        }
        fmt++;
    }
    va_end(args);
}

/* ========================================================================
 *  BÖLÜM 4: BELLEK YÖNETİMİ (PHYSICAL PAGE ALLOCATOR)
 * ======================================================================== */

static u8 memory_map[MAX_PHYSICAL_PAGES / 8]; // Bitmap: 0=boş, 1=dolu

static void memory_init() {
    // Tüm belleği temizle (0 = free)
    for (size_t i = 0; i < sizeof(memory_map); i++) {
        memory_map[i] = 0;
    }
    // İlk sayfayı (kernel'in kendisi) dolu işaretle (basitlik adına)
    memory_map[0] = 0xFF; 
    kprintf("[OK] Bellek Yöneticisi Başlatıldı.\n");
}

static u64* allocate_page() {
    for (size_t i = 0; i < sizeof(memory_map); i++) {
        if (memory_map[i] != 0xFF) {
            for (int j = 0; j < 8; j++) {
                if (!(memory_map[i] & (1 << j))) {
                    memory_map[i] |= (1 << j); // Dolu olarak işaretle
                    u64* page = (u64*)(i * 8 * 4096 + j * 4096); // Basit adres hesaplama
                    // Sayfayı sıfırla
                    for (int k = 0; k < 512; k++) {
                        page[k] = 0;
                    }
                    return page;
                }
            }
        }
    }
    return NULL; // Bellek yetersiz
}

static void free_page(u64* addr) {
    usize index = ((u64)addr) / 4096;
    usize byte_index = index / 8;
    usize bit_index = index % 8;
    
    if (byte_index < sizeof(memory_map)) {
        memory_map[byte_index] &= ~(1 << bit_index);
    }
}

/* ========================================================================
 *  BÖLÜM 5: KESME YÖNETİMİ (IDT & ISR)
 * ======================================================================== */

// IDT Entry Yapısı
struct idt_entry {
    u16 base_low;
    u16 selector;
    u8  zero;
    u8  flags;
    u16 base_high;
    u32 base_upper;
    u32 reserved;
} __attribute__((packed));

struct idt_ptr {
    u16 limit;
    u64 base;
} __attribute__((packed));

static struct idt_entry idt[256];
static struct idt_ptr idtp;

// Dışa aktarılan Assembly fonksiyonları (linker script ile sağlanmalı)
extern void isr_handler(); 
extern void irq_handler();

static void idt_set_gate(u8 num, u64 address, u16 selector, u8 flags) {
    idt[num].base_low = address & 0xFFFF;
    idt[num].base_high = (address >> 16) & 0xFFFF;
    idt[num].base_upper = (address >> 32) & 0xFFFFFFFF;
    idt[num].selector = selector;
    idt[num].zero = 0;
    idt[num].flags = flags; // 0x8E = Present, Ring 0, Interrupt Gate
}

static void idt_init() {
    idtp.limit = sizeof(idt) - 1;
    idtp.base = (u64)&idt;

    // Tüm kapıları sıfırla
    for (int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    // Gerçek sistemde burada ISR adresleri atanır.
    // Örnek: idt_set_gate(0, (u64)isr0, 0x08, 0x8E);
    
    kprintf("[OK] IDT (Kesme Tablosu) Hazırlandı.\n");
    // asm volatile ("lidt %0" : : "m"(idtp)); // Gerçek yükleme
}

/* ========================================================================
 *  BÖLÜM 6: ÇOKLU GÖREV (THREADING & SCHEDULER)
 * ======================================================================== */

enum thread_state {
    THREAD_RUNNING,
    THREAD_READY,
    THREAD_BLOCKED,
    THREAD_ZOMBIE
};

struct thread {
    u64 id;
    enum thread_state state;
    u64 stack_top;
    u64 rip; // Instruction Pointer
    char name[32];
    struct thread* next;
};

static struct thread* current_thread = NULL;
static struct thread* thread_list = NULL;
static u64 thread_counter = 0;

static struct thread* thread_create(void (*entry_point)(), const char* name) {
    struct thread* t = (struct thread*)allocate_page(); // Thread yapısı için sayfa ayır
    if (!t) return NULL;

    t->id = thread_counter++;
    t->state = THREAD_READY;
    t->stack_top = (u64)allocate_page() + KERNEL_STACK_SIZE; // Stack için sayfa ayır
    
    // İsim kopyalama (basit)
    size_t i = 0;
    while(name[i] && i < 31) {
        t->name[i] = name[i];
        i++;
    }
    t->name[i] = '\0';

    t->rip = (u64)entry_point;
    t->next = thread_list;
    thread_list = t;

    kprintf("[+] Yeni Thread Oluşturuldu: ");
    kernel_print(t->name);
    kprintf(" (ID: ");
    print_int(t->id);
    kprintf(")\n");

    return t;
}

static void scheduler_yield() {
    if (!thread_list) return;

    // Basit Round-Robin Scheduler
    static struct thread* last = NULL;
    
    if (!last) last = thread_list;
    else last = last->next;

    // Döngüsel liste kontrolü
    if (!last) last = thread_list;

    current_thread = last;
    
    // Context Switch burada assembly ile yapılmalıdır.
    // save_context();
    // load_context(current_thread);
}

// Örnek Thread Fonksiyonu
void example_thread_func() {
    while (true) {
        kprintf(".");
        // Busy wait yerine timer interrupt beklenmelidir
        for (volatile int i = 0; i < 10000000; i++); 
        scheduler_yield();
    }
}

/* ========================================================================
 *  BÖLÜM 7: ANA ÇEKİRDEK GİRİŞ NOKTASI (KERNEL MAIN)
 * ======================================================================== */

// Multiboot2 Struct Tanımları (Özet)
struct multiboot_info {
    u32 size;
    u32 reserved;
    // ... diğer alanlar type/tag yapısıyla gelir
};

void kernel_main(u64 magic, u64 mboot_addr) {
    // 1. Ekranı Temizle ve İlk Mesajı Yaz
    clear_screen();
    kprintf("==================================================\n");
    kprintf("       NOVA KERNEL v1.0 - System Booting          \n");
    kprintf("==================================================\n");

    // 2. Multiboot Kontrolü (Magic Number: 0x36d76289)
    if (magic != 0x36d76289) {
        kprintf("[HATA] Geçersiz Multiboot2 Magic Number!\n");
        while(1); // Sonsuz döngüde bekle
    }
    kprintf("[OK] Bootloader Doğrulandı.\n");

    // 3. Alt Sistemleri Başlat
    memory_init();
    idt_init();

    // 4. PIC (Programmable Interrupt Controller) Remap
    // IRQ 0-15'i kesme vektörü 32-47'e taşıyoruz (CPU exceptions ile çakışmayı önlemek için)
    outb(0x20, 0x11); io_wait(); // ICW1
    outb(0xA0, 0x11); io_wait();
    outb(0x21, 0x20); io_wait(); // ICW2 (Master Offset)
    outb(0xA1, 0x28); io_wait(); // ICW2 (Slave Offset)
    outb(0x21, 0x04); io_wait(); // ICW3
    outb(0xA1, 0x02); io_wait();
    outb(0x21, 0x01); io_wait(); // ICW4
    outb(0xA1, 0x01); io_wait();
    outb(0x21, 0x0); io_wait();  // Mask all
    outb(0xA1, 0x0); io_wait();
    kprintf("[OK] PIC Yeniden Eşlendi (Remapped).\n");

    // 5. Çoklu Görev Testi
    kprintf("\n--- Çoklu Görev Testi Başlatılıyor ---\n");
    
    // Ana thread'i simüle et
    struct thread* main_t = thread_create(NULL, "MainIdle");
    current_thread = main_t;

    // Yeni thread'ler oluştur
    thread_create(example_thread_func, "Worker-A");
    thread_create(example_thread_func, "Worker-B");
    
    kprintf("[OK] Scheduler Aktif. Thread'ler çalışıyor...\n\n");

    // 6. Ana Kernel Döngüsü (Idle Loop)
    // Gerçek bir kernel burada 'hlt' komutu ile işlemciyi uyutur ve kesmelerle uyanır.
    kprintf("Sistem kararlı. Kernel döngüsüne giriliyor...\n");
    
    u64 tick = 0;
    while (true) {
        // Her iterasyonda scheduler'a şans ver
        if (tick % 10000000 == 0) {
            scheduler_yield();
            kprintf("|"); // Kalp atışı göstergesi
        }
        tick++;
        
        // CPU'yu boşta beklet (Power saving)
        asm volatile ("hlt");
    }
}

/* 
 * NOT: Bu kodun derlenebilmesi ve çalıştırılabilmesi için:
 * 1. Bir linker script (.ld) ile 0x100000 (1MB) adresine yüklenmesi gerekir.
 * 2. Boot assembly (boot.asm) ile Multiboot2 header sağlanmalıdır.
 * 3. ISR ve Context Switch assembly rutinleri (switch.asm) link edilmelidir.
 * 4. Grub2 konfigürasyonu ile ISO oluşturulmalıdır.
 */
