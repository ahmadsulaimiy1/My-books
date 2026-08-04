'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, EmptyState } from '@/components/portal/ui';

export default function LibraryView({ items: allItems }) {
  const [typeFilter, setTypeFilter] = useState('All');
  const types = ['All', ...new Set(allItems.map((l) => l.type))];
  const items = allItems.filter((l) => typeFilter === 'All' || l.type === typeFilter);

  return (
    <PortalShell role="student" active="library" title="Library">
      <div className="filters" role="group" aria-label="Filter library items by type">
        {types.map((t) => (
          <button
            key={t}
            type="button"
            className={t === typeFilter ? 'chip active' : 'chip'}
            aria-pressed={t === typeFilter}
            onClick={() => setTypeFilter(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <Card>
          <EmptyState message="No library items match this filter." />
        </Card>
      ) : (
        <div className="grid">
          {items.map((item) => (
            <Card key={item.id} className="item-card">
              <div className="item-head">
                <Badge tone="info">{item.type}</Badge>
              </div>
              <h3>{item.title}</h3>
              <p className="course-tag">Related course: {item.course}</p>
            </Card>
          ))}
        </div>
      )}

      <style jsx>{`
        .filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
        .chip { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 7px 16px; font-size: 13px; font-weight: 600; color: var(--ink-muted); cursor: pointer; }
        .chip:hover { background: var(--manuscript); }
        .chip.active { background: var(--navy); border-color: var(--navy); color: #fff; }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
        .item-card :global(.pcard-body) { display: flex; flex-direction: column; gap: 8px; }
        .item-head { margin-bottom: 4px; }
        .item-card h3 { font-family: 'Fraunces', serif; font-size: 15.5px; color: var(--navy); margin: 0; }
        .course-tag { font-size: 12.5px; color: var(--ink-muted); margin: 0; }
      `}</style>
    </PortalShell>
  );
}
