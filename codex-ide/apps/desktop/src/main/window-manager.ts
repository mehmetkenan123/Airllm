/**
 * Window Manager - Manages multiple windows and tabs
 */

import { BrowserWindow, BrowserWindowConstructorOptions } from 'electron';

interface WindowConfig extends BrowserWindowConstructorOptions {
  id?: string;
  type?: 'main' | 'dialog' | 'preview';
}

export class WindowManager {
  private windows: Map<string, BrowserWindow> = new Map();
  private activeWindowId: string | null = null;

  /**
   * Create a new window
   */
  createWindow(config: WindowConfig = {}): BrowserWindow {
    const id = config.id || `window-${Date.now()}`;
    
    const window = new BrowserWindow({
      ...config,
      frame: config.frame ?? false,
      backgroundColor: '#1e1e1e',
      trafficLightPosition: { x: 10, y: 10 },
    });

    this.windows.set(id, window);
    this.activeWindowId = id;

    window.on('focus', () => {
      this.activeWindowId = id;
    });

    window.on('closed', () => {
      this.windows.delete(id);
      if (this.activeWindowId === id) {
        this.activeWindowId = null;
      }
    });

    return window;
  }

  /**
   * Get window by ID
   */
  getWindow(id: string): BrowserWindow | undefined {
    return this.windows.get(id);
  }

  /**
   * Get active window
   */
  getActiveWindow(): BrowserWindow | null {
    if (!this.activeWindowId) return null;
    return this.windows.get(this.activeWindowId) || null;
  }

  /**
   * Focus a window
   */
  focusWindow(id: string): void {
    const window = this.windows.get(id);
    if (window) {
      window.focus();
      this.activeWindowId = id;
    }
  }

  /**
   * Close a window
   */
  closeWindow(id: string): void {
    const window = this.windows.get(id);
    if (window) {
      window.close();
    }
  }

  /**
   * Close all windows
   */
  closeAll(): void {
    for (const window of this.windows.values()) {
      window.close();
    }
    this.windows.clear();
    this.activeWindowId = null;
  }

  /**
   * Get all windows
   */
  getAllWindows(): BrowserWindow[] {
    return Array.from(this.windows.values());
  }

  /**
   * Get window count
   */
  getWindowCount(): number {
    return this.windows.size;
  }

  /**
   * Create a dialog window
   */
  createDialog(options: {
    title: string;
    width: number;
    height: number;
    modal?: boolean;
  }): BrowserWindow {
    const parent = this.getActiveWindow();
    
    return this.createWindow({
      id: `dialog-${Date.now()}`,
      type: 'dialog',
      width: options.width,
      height: options.height,
      title: options.title,
      modal: options.modal ?? true,
      parent: parent || undefined,
      resizable: false,
      movable: true,
      minimizable: false,
      maximizable: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      },
    });
  }
}
