import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import App from './App';
import { mockScans } from './mock/mockData';

describe('AgroLens Research Dashboard Tests', () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        scans: mockScans.map((scan) => ({
          scan_id: scan.scan_id,
          scan_timestamp: scan.timestamp,
          crop: scan.crop,
          disease_label: scan.predicted_disease,
          confidence: scan.confidence,
          verification_status: scan.verification_status,
          latitude: scan.location?.lat ?? null,
          longitude: scan.location?.lon ?? null,
          location_consent: Boolean(scan.location),
        })),
      }),
    });
    render(<App />);
  });

  it('renders the backend-connected research dashboard', () => {
    expect(screen.getByText(/AgroLens:/i)).toBeInTheDocument();
    expect(screen.getByText(/LIVE API DATA|LOADING BACKEND DATA/i)).toBeInTheDocument();
  });

  it('separates farmer confirmation and expert verification correctly in aggregate metrics', () => {
    // Total scans: 7
    expect(screen.getByText('7')).toBeInTheDocument();
    // Unique crops: 5
    expect(screen.getByText('5')).toBeInTheDocument();
    // Low confidence (< 0.60): 2
    expect(screen.getByText('2')).toBeInTheDocument();
    // Farmer confirmed: 4
    expect(screen.getByText('4')).toBeInTheDocument();
    // Expert verified: 3
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('filters scan records when a crop is selected', async () => {
    const user = userEvent.setup();
    const cropSelect = screen.getByDisplayValue('All Crops');

    await user.selectOptions(cropSelect, 'Tomato');

    expect(screen.getByText('scan_101')).toBeInTheDocument();
    expect(screen.getByText('scan_102')).toBeInTheDocument();
    expect(screen.queryByText('scan_103')).not.toBeInTheDocument();
  });

  it('filters by verification status', async () => {
    const user = userEvent.setup();
    const statusSelect = screen.getByDisplayValue('All Verification States');

    await user.selectOptions(statusSelect, 'rejected');

    expect(screen.getByText('scan_106')).toBeInTheDocument();
    expect(screen.queryByText('scan_101')).not.toBeInTheDocument();
  });

  it('filters by minimum confidence threshold', () => {
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.90' } });

    expect(screen.getByText('scan_101')).toBeInTheDocument();
    expect(screen.getByText('scan_105')).toBeInTheDocument();
    expect(screen.queryByText('scan_103')).not.toBeInTheDocument();
  });

  it('handles optional location coordinates safely in detail modal', async () => {
    const user = userEvent.setup();
    const viewButtons = screen.getAllByRole('button', { name: /View Details/i });

    // Open scan_101 (has location)
    await user.click(viewButtons[0]);
    expect(screen.getAllByText(/14\.62, 74\.83/).length).toBeGreaterThan(0);

    // Close modal
    await user.click(screen.getByRole('button', { name: /Close/i }));

    // Open scan_102 (location is null)
    await user.click(viewButtons[1]);
    expect(screen.getAllByText('Not provided').length).toBeGreaterThan(0);
  });
});