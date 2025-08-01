import React from 'react';
import { clsx } from 'clsx';

interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  timestamp: string;
  status?: 'completed' | 'current' | 'pending';
  icon?: string;
}

interface PxTimelineProps {
  items: TimelineItem[];
  className?: string;
}

export const PxTimeline: React.FC<PxTimelineProps> = ({ items, className }) => {
  return (
    <div className={clsx('relative', className)}>
      {items.map((item, index) => (
        <div key={item.id} className="relative flex gap-4 pb-8 last:pb-0">
          {/* Timeline Line */}
          {index < items.length - 1 && (
            <div className="absolute left-4 top-8 w-0.5 h-full bg-gray-300" />
          )}
          
          {/* Timeline Dot */}
          <div
            className={clsx(
              'relative flex-shrink-0 w-8 h-8 clip-px border-px flex items-center justify-center font-pixel text-xs',
              {
                'bg-electric-teal border-ink text-ink': item.status === 'completed',
                'bg-primary border-ink text-ink animate-px-glow': item.status === 'current',
                'bg-gray-200 border-gray-400 text-gray-600': item.status === 'pending',
              }
            )}
          >
            {item.icon || (index + 1)}
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-pixel text-sm text-ink">{item.title}</h3>
              <span className="text-xs text-gray-500 font-body">
                {item.timestamp}
              </span>
            </div>
            {item.description && (
              <p className="text-sm text-gray-700 leading-relaxed">
                {item.description}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

// Application Timeline variant
interface ApplicationTimelineProps {
  applicationStatus: 'applied' | 'reviewing' | 'interviewing' | 'accepted' | 'rejected';
  applicationDate: string;
  lastUpdate: string;
  className?: string;
}

export const PxApplicationTimeline: React.FC<ApplicationTimelineProps> = ({
  applicationStatus,
  applicationDate,
  lastUpdate,
  className,
}) => {
  const getTimelineItems = (): TimelineItem[] => {
    const baseItems: TimelineItem[] = [
      {
        id: 'applied',
        title: 'APPLICATION SUBMITTED',
        description: 'Your application has been received',
        timestamp: applicationDate,
        status: 'completed',
        icon: '📝',
      },
      {
        id: 'reviewing',
        title: 'UNDER REVIEW',
        description: 'Organization is reviewing your application',
        timestamp: lastUpdate,
        status: applicationStatus === 'applied' ? 'current' : 'completed',
        icon: '👀',
      },
      {
        id: 'decision',
        title: 'DECISION MADE',
        description: 'Organization has made a decision',
        timestamp: applicationStatus === 'accepted' || applicationStatus === 'rejected' ? lastUpdate : 'Pending',
        status: applicationStatus === 'accepted' || applicationStatus === 'rejected' ? 'completed' : 'pending',
        icon: applicationStatus === 'accepted' ? '✅' : applicationStatus === 'rejected' ? '❌' : '⏳',
      },
    ];

    if (applicationStatus === 'interviewing') {
      baseItems.splice(2, 0, {
        id: 'interviewing',
        title: 'INTERVIEW SCHEDULED',
        description: 'You have been selected for an interview',
        timestamp: lastUpdate,
        status: 'current',
        icon: '🗣️',
      });
    }

    return baseItems;
  };

  return (
    <div className={className}>
      <h3 className="font-pixel text-ink mb-4">APPLICATION PROGRESS</h3>
      <PxTimeline items={getTimelineItems()} />
    </div>
  );
};