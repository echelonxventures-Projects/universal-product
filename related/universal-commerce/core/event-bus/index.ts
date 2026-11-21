import { UCIIEvent, EventType } from '../types/event';

interface EventSubscription {
  event: EventType;
  handler: (event: UCIIEvent) => Promise<void> | void;
  sync?: boolean;
}

interface PendingEvent {
  event: UCIIEvent;
  retries: number;
  maxRetries: number;
}

export class EventBus implements EventPublisher, EventSubscriber {
  private subscriptions: EventSubscription[] = [];
  private queue: PendingEvent[] = [];
  private processing: Map<string, boolean> = new Map();

  subscribe(eventType: EventType, handler: (event: UCIIEvent) => void): void {
    this.subscriptions.push({ event: eventType, handler, sync: true });
  }

  async publish(event: UCIIEvent): Promise<void> {
    const matching = this.subscriptions.filter(s => s.event === event.type);
    
    for (const sub of matching) {
      try {
        await sub.handler(event);
      } catch (err) {
        console.error(`Handler failed for ${event.type}:`, err);
      }
    }
  }

  async publishAsync(event: UCIIEvent): Promise<void> {
    const matching = this.subscriptions.filter(s => s.event === event.type && !s.sync);
    
    for (const sub of matching) {
      try {
        await sub.handler(event);
      } catch (err) {
        console.error(`Async handler failed for ${event.type}:`, err);
      }
    }
  }

  async consumeQueue(): Promise<void> {
    while (this.queue.length > 0) {
      const pending = this.queue.shift();
      if (!pending) continue;
      
      if (pending.retries >= pending.maxRetries) {
        console.error(`Max retries exceeded for event ${pending.event.id}`);
        continue;
      }

      try {
        await this.publish(pending.event);
        pending.retries++;
        this.queue.push(pending);
      } catch (err) {
        pending.retries++;
        this.queue.push(pending);
      }
    }
  }
}

export const bus = new EventBus();
