import React, { Suspense, lazy, useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import { ErrorBoundary } from 'react-error-boundary';

// Lazy loaded components for performance
const TitleBar = lazy(() => import('./TitleBar'));
const ActivityBar = lazy(() => import('./ActivityBar'));
const Sidebar = lazy(() => import('./Sidebar'));
const EditorArea = lazy(() => import('./EditorArea'));
const StatusBar = lazy(() => import('./StatusBar'));
const CommandPalette = lazy(() => import('../components/CommandPalette'));
const QuickFileOpen = lazy(() => import('../components/QuickFileOpen'));

interface AppShellProps {
  initialTheme?: 'dark' | 'light';
}

const AppShell: React.FC<AppShellProps> = ({ initialTheme = 'dark' }) => {
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [panelVisible, setPanelVisible] = useState(true);
  const [terminalVisible, setTerminalVisible] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [quickFileOpen, setQuickFileOpen] = useState(false);
  const [activePanel, setActivePanel] = useState<'explorer' | 'search' | 'git' | 'debug' | 'extensions' | 'ai'>('explorer');

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCtrl = e.ctrlKey || e.metaKey;
      
      if (isCtrl && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      } else if (isCtrl && e.key === 'p') {
        e.preventDefault();
        setQuickFileOpen(true);
      } else if (isCtrl && e.key === 'b') {
        e.preventDefault();
        setSidebarVisible(prev => !prev);
      } else if (isCtrl && e.key === 'j') {
        e.preventDefault();
        setPanelVisible(prev => !prev);
      } else if (isCtrl && e.key === '`') {
        e.preventDefault();
        setTerminalVisible(prev => !prev);
      } else if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
        setQuickFileOpen(false);
      } else if (isCtrl && e.shiftKey && e.key === 'i') {
        e.preventDefault();
        setActivePanel('ai');
        setSidebarVisible(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarVisible(prev => !prev);
  }, []);

  const togglePanel = useCallback(() => {
    setPanelVisible(prev => !prev);
  }, []);

  const toggleTerminal = useCallback(() => {
    setTerminalVisible(prev => !prev);
  }, []);

  return (
    <ErrorBoundary fallback={<div>Kritik hata oluştu</div>}>
      <AppShellContainer className="app-shell">
        <TitleBar 
          onMenuToggle={toggleSidebar}
          aiStatus="ready"
        />
        
        <MainContent $sidebarVisible={sidebarVisible}>
          <ActivityBar 
            activePanel={activePanel}
            onPanelChange={setActivePanel}
          />
          
          {sidebarVisible && (
            <Sidebar 
              activePanel={activePanel}
              onClose={toggleSidebar}
            />
          )}
          
          <EditorArea 
            panelVisible={panelVisible}
            terminalVisible={terminalVisible}
          />
        </MainContent>
        
        {panelVisible && (
          <BottomPanel $terminalVisible={terminalVisible}>
            {/* Panel content */}
          </BottomPanel>
        )}
        
        <StatusBar 
          onTerminalToggle={toggleTerminal}
          terminalVisible={terminalVisible}
        />
        
        <Suspense fallback={<LoadingOverlay />}>
          {commandPaletteOpen && (
            <CommandPalette onClose={() => setCommandPaletteOpen(false)} />
          )}
          {quickFileOpen && (
            <QuickFileOpen onClose={() => setQuickFileOpen(false)} />
          )}
        </Suspense>
      </AppShellContainer>
    </ErrorBoundary>
  );
};

const LoadingOverlay = () => (
  <LoadingContainer>
    <div className="spinner" />
    <span>Yükleniyor...</span>
  </LoadingContainer>
);

const AppShellContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--bg-deepest);
  color: var(--text-primary);
`;

const MainContent = styled.div<{ $sidebarVisible: boolean }>`
  display: flex;
  flex: 1;
  overflow: hidden;
  transition: all var(--transition-normal);
`;

const BottomPanel = styled.div<{ $terminalVisible: boolean }>`
  height: ${props => props.$terminalVisible ? '300px' : '200px'};
  border-top: 1px solid var(--border-default);
  background: var(--bg-surface);
  transition: height var(--transition-normal);
`;

const LoadingContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-deepest);
  z-index: 9999;
  
  .spinner {
    width: 48px;
    height: 48px;
    border: 3px solid var(--border-subtle);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

export default AppShell;
