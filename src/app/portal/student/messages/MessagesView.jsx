'use client';

import PortalShell from '@/components/portal/PortalShell';
import MessageInbox from '@/components/portal/MessageInbox';

export default function MessagesView({ messages }) {
  return (
    <PortalShell role="student" active="messages" title="Messages">
      <MessageInbox messages={messages} />
    </PortalShell>
  );
}
