'use client';

import PortalShell from '@/components/portal/PortalShell';
import MessageInbox from '@/components/portal/MessageInbox';

export default function FacultyMessagesView({ messages }) {
  return (
    <PortalShell role="faculty" active="messages" title="Messages">
      <MessageInbox messages={messages} />
    </PortalShell>
  );
}
