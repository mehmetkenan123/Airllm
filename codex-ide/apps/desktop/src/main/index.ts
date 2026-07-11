/**
 * Codex IDE - Electron Main Process Entry Point
 * Manages BrowserWindow, IPC handlers, and application lifecycle
 */

import { app, BrowserWindow, ipcMain, shell } from 'electron';
import * as path from 'path';
import { WindowManager } from './window-manager.js';
import { setupIPCHandlers } from './ipc-handlers.js';
import { MenuBuilder } from './menu-builder.js';
import { setupShortcuts } from './shortcuts.js';
import { TrayManager } from './tray.js';
import { Logger } from './logger.js';
import { SessionManager } from './session-manager.js';

const logger = new Logger('Main');
let mainWindow: BrowserWindow | null = null;
let windowManager: WindowManager | null = null;
let trayManager: TrayManager | null = null;
let sessionManager: SessionManager | null = null;

// Disable GPU acceleration for low-end systems if needed
if (process.env.CODEX_DISABLE_GPU) {
  app.disableHardwareAcceleration();
}

app.whenReady().then(async () => {
  logger.info('Codex IDE starting...');
  
  // Initialize session manager
  sessionManager = new SessionManager();
  await sessionManager.initialize();

  // Create main window
  createMainWindow();

  // Setup IPC handlers
  setupIPCHandlers();

  // Build menu
  const menuBuilder = new MenuBuilder();
  menuBuilder.build();

  // Setup global shortcuts
  setupShortcuts();

  // Setup system tray
  trayManager = new TrayManager();
  trayManager.create();

  logger.info('Codex IDE ready');
});

function createMainWindow(): void {
  windowManager = new WindowManager();
  
  mainWindow = windowManager.createWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: 'Codex IDE',
    show: false, // Show when ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, '../preload/index.js'),
      sandbox: true,
    },
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
    mainWindow?.focus();
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    windowManager = null;
  });
}

// App lifecycle events
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

app.on('before-quit', async (event) => {
  event.preventDefault();
  
  // Save session state
  if (sessionManager) {
    await sessionManager.save();
  }
  
  // Close all windows gracefully
  const windows = BrowserWindow.getAllWindows();
  for (const win of windows) {
    win.close();
  }
  
  app.exit(0);
});

// IPC handlers for main process
ipcMain.handle('app:get-version', () => {
  return app.getVersion();
});

ipcMain.handle('app:get-platform', () => {
  return process.platform;
});

ipcMain.handle('app:minimize', () => {
  mainWindow?.minimize();
});

ipcMain.handle('app:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.handle('app:close', () => {
  mainWindow?.close();
});
