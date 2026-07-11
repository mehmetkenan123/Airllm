import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

interface TitleBarProps {
  onMenuToggle: () => void;
  aiStatus: 'ready' | 'thinking' | 'error' | 'offline';
}

const TitleBar: React.FC<TitleBarProps> = ({ onMenuToggle, aiStatus }) => {
  const [projectName, setProjectName] = useState('Codex IDE');
  const [workspacePath, setWorkspacePath] = useState('/workspace/codex-ide');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getAIStatusColor = () => {
    switch (aiStatus) {
      case 'ready': return '#00e676';
      case 'thinking': return '#00d4ff';
      case 'error': return '#ff1744';
      case 'offline': return '#606080';
    }
  };

  const handleDoubleClick = () => {
    // Maximize/restore window logic would go here
    console.log('Double click - toggle maximize');
  };

  return (
    <TitleBarContainer appRegion="drag" onDoubleClick={handleDoubleClick}>
      <LeftSection>
        <MenuButton onClick={onMenuToggle} appRegion="no-drag">
          <HamburgerIcon>
            <span></span>
            <span></span>
            <span></span>
          </HamburgerIcon>
        </MenuButton>
        
        <WindowTitle>
          <ProjectName>{projectName}</ProjectName>
          <WorkspacePath>{workspacePath}</WorkspacePath>
        </WindowTitle>
      </LeftSection>

      <CenterSection appRegion="no-drag">
        <QuickAction title="Run (F5)">▶ Run</QuickAction>
        <QuickAction title="Debug (F9)">🐛 Debug</QuickAction>
        <QuickAction title="Build (Ctrl+Shift+B)">⚙ Build</QuickAction>
        <QuickAction title="Format (Shift+Alt+F)">✨ Format</QuickAction>
      </CenterSection>

      <RightSection appRegion="no-drag">
        <AIStatusIndicator $statusColor={getAIStatusColor()}>
          <StatusDot $color={getAIStatusColor()} />
          <StatusText>
            {aiStatus === 'ready' && 'Llama-3-8B'}
            {aiStatus === 'thinking' && 'Düşünüyor...'}
            {aiStatus === 'error' && 'Hata'}
            {aiStatus === 'offline' && 'Offline'}
          </StatusText>
        </AIStatusIndicator>
        
        <TimeDisplay>{currentTime.toLocaleTimeString()}</TimeDisplay>
        
        <WindowControls>
          <ControlButton className="minimize" title="Minimize">─</ControlButton>
          <ControlButton className="maximize" title="Maximize">□</ControlButton>
          <ControlButton className="close" title="Close">×</ControlButton>
        </WindowControls>
      </RightSection>
    </TitleBarContainer>
  );
};

const TitleBarContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  background: linear-gradient(135deg, var(--bg-deepest) 0%, var(--bg-deep) 100%);
  backdrop-filter: blur(var(--glass-blur));
  border-bottom: 1px solid var(--border-subtle);
  -webkit-app-region: drag;
  user-select: none;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 12px;
`;

const MenuButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
  -webkit-app-region: no-drag;

  &:hover {
    background: var(--bg-surface);
  }
`;

const HamburgerIcon = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  
  span {
    display: block;
    width: 16px;
    height: 2px;
    background: currentColor;
    border-radius: 1px;
    transition: all var(--transition-fast);
  }
`;

const WindowTitle = styled.div`
  display: flex;
  flex-direction: column;
`;

const ProjectName = styled.span`
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
`;

const WorkspacePath = styled.span`
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.7;
`;

const CenterSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const QuickAction = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: var(--bg-elevated);
    color: var(--text-primary);
    border-color: var(--border-accent);
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding-right: 12px;
`;

const AIStatusIndicator = styled.div<{ $statusColor: string }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-surface);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
`;

const StatusDot = styled.div<{ $color: string }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$color};
  box-shadow: 0 0 8px ${props => props.$color}66;
  animation: ${props => props.$color === '#00d4ff' ? 'pulse 1.5s infinite' : 'none'};

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const StatusText = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
`;

const TimeDisplay = styled.span`
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
`;

const WindowControls = styled.div`
  display: flex;
  gap: 0;
`;

const ControlButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 16px;
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: var(--bg-surface);
    color: var(--text-primary);
  }

  &.close:hover {
    background: var(--accent-error);
    color: white;
  }
`;

export default TitleBar;
