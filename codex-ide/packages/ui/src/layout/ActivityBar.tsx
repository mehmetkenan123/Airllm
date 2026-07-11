import React from 'react';
import styled from 'styled-components';

type PanelType = 'explorer' | 'search' | 'git' | 'debug' | 'extensions' | 'ai' | 'settings' | 'account';

interface ActivityBarProps {
  activePanel: PanelType;
  onPanelChange: (panel: PanelType) => void;
}

interface ActivityItem {
  id: PanelType;
  icon: string;
  label: string;
  badge?: number;
}

const ActivityBar: React.FC<ActivityBarProps> = ({ activePanel, onPanelChange }) => {
  const activities: ActivityItem[] = [
    { id: 'explorer', icon: '📁', label: 'Explorer' },
    { id: 'search', icon: '🔍', label: 'Search' },
    { id: 'git', icon: '🔗', label: 'Source Control' },
    { id: 'debug', icon: '🐛', label: 'Debug' },
    { id: 'extensions', icon: '🧩', label: 'Extensions' },
    { id: 'ai', icon: '🤖', label: 'AI Chat' },
  ];

  const bottomActivities: ActivityItem[] = [
    { id: 'settings', icon: '⚙️', label: 'Settings' },
    { id: 'account', icon: '👤', label: 'Account' },
  ];

  const handleActivityClick = (id: PanelType) => {
    onPanelChange(id);
  };

  return (
    <ActivityBarContainer>
      <TopActivities>
        {activities.map(activity => (
          <ActivityItem
            key={activity.id}
            $active={activePanel === activity.id}
            onClick={() => handleActivityClick(activity.id)}
            title={activity.label}
          >
            <ActivityIcon $isAI={activity.id === 'ai'}>
              {activity.icon}
            </ActivityIcon>
            {activity.badge !== undefined && activity.badge > 0 && (
              <Badge>{activity.badge}</Badge>
            )}
          </ActivityItem>
        ))}
      </TopActivities>

      <BottomActivities>
        {bottomActivities.map(activity => (
          <ActivityItem
            key={activity.id}
            $active={activePanel === activity.id}
            onClick={() => handleActivityClick(activity.id)}
            title={activity.label}
          >
            <ActivityIcon>{activity.icon}</ActivityIcon>
          </ActivityItem>
        ))}
      </BottomActivities>
    </ActivityBarContainer>
  );
};

const ActivityBarContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 48px;
  background: var(--bg-deep);
  border-right: 1px solid var(--border-subtle);
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 0;
  }
`;

const TopActivities = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
`;

const BottomActivities = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 8px;
  border-top: 1px solid var(--border-subtle);
  margin-top: auto;
`;

const ActivityItem = styled.div<{ $active: boolean }>`
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  cursor: pointer;
  transition: all var(--transition-fast);
  
  &:hover {
    transform: scale(1.1);
  }
  
  ${props => props.$active && `
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 2px;
      background: white;
      box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
    
    &::after {
      content: '';
      position: absolute;
      inset: 4px;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border-radius: var(--radius-sm);
      opacity: 0.2;
    }
  `}
`;

const ActivityIcon = styled.div<{ $isAI?: boolean }>`
  font-size: 20px;
  z-index: 1;
  filter: grayscale(0.3);
  transition: filter var(--transition-fast);
  
  ${props => props.$isAI && `
    filter: drop-shadow(0 0 4px var(--accent-ai));
  `}
  
  &:hover {
    filter: grayscale(0);
  }
`;

const Badge = styled.span`
  position: absolute;
  top: 8px;
  right: 8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: var(--accent-error);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
`;

export default ActivityBar;
