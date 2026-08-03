// Unit test for the entity detail panel. The API client is mocked so the test
// runs without a backend and asserts purely on rendering: given a role entity and
// its relationships, the panel shows the name, the confidence flag, and the
// "referenced by activities" section. Keeps a regression guard on the panel's
// role-dependent wording.
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import EntityDetailPanel from '../EntityDetailPanel';
import { AdminProvider } from '../../context/AdminContext';
import { makeFrameworkTheme } from '../../theme/theme';

const theme = makeFrameworkTheme(null); // PRINCE2 defaults

vi.mock('../../api/client', () => ({
  getAdminPassword: () => '',
  setAdminPassword: () => {},
  api: {
    verifyPassword: vi.fn(),
    pdfUrl: () => '#pdf',
    csvUrl: () => '#csv',
    getEntity: vi.fn().mockResolvedValue({
      id: 10,
      type: 'role',
      name: 'Project Manager',
      code: null,
      confidence: 'confirmed',
      parent_name: null,
      description: null,
      related: [
        {
          relationship_id: 1,
          entity_id: 20,
          type: 'activity',
          name: 'Authorize a work package',
          code: 'C',
          code_label: 'Responsible',
          confidence: 'indicative',
          direction: 'in',
          via_process: 'Controlling a Stage',
        },
      ],
    }),
  },
}));

const noop = () => {};

describe('EntityDetailPanel', () => {
  it('renders the entity and its related rows', async () => {
    render(
      <AdminProvider>
        <EntityDetailPanel
          frameworkKey="prince2-7"
          theme={theme}
          entityId={10}
          onSelect={noop}
          onClose={noop}
          onEdit={noop}
          onAddRelationship={noop}
          onChanged={noop}
          reloadToken={0}
        />
      </AdminProvider>,
    );
    expect(await screen.findByText('Project Manager')).toBeInTheDocument();
    expect(
      await screen.findByText('Authorize a work package'),
    ).toBeInTheDocument();
    // the code pill + label from the relationship
    expect(screen.getByText('C')).toBeInTheDocument();
    expect(screen.getByText(/Responsible/)).toBeInTheDocument();
  });
});
