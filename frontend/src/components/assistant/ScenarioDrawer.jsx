import React, { useState, useEffect } from 'react';
import { SlidersHorizontal, MapPin, Calendar, FileText, AlertTriangle } from 'lucide-react';
import { fetchDocuments } from '../../services/api';

export default function ScenarioDrawer({ scenario, onChange }) {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetchDocuments()
      .then((docs) => setDocuments(docs || []))
      .catch(() => setDocuments([]));
  }, []);

  return (
    <div className="scenario-drawer">
      <div className="scenario-drawer-header">
        <SlidersHorizontal size={15} />
        <span>Scenario Parameters &amp; Policy Metadata</span>
      </div>

      <div className="scenario-grid">
        <div className="scenario-field">
          <label className="scenario-label">
            <FileText size={13} />
            <span>Policy Form / Target Doc</span>
          </label>
          <select
            className="scenario-select"
            value={scenario.policy_type || ''}
            onChange={(e) => onChange('policy_type', e.target.value)}
          >
            <option value="">
              {documents.length > 0 ? 'Any / All Ingested Policies (Default)' : 'Any Policy (No Ingested Documents)'}
            </option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.id} {doc.filename ? `(${doc.filename})` : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="scenario-field">
          <label className="scenario-label">
            <MapPin size={13} />
            <span>Jurisdiction</span>
          </label>
          <select
            className="scenario-select"
            value={scenario.jurisdiction || ''}
            onChange={(e) => onChange('jurisdiction', e.target.value)}
          >
            <option value="">Any Jurisdiction (Optional)</option>
            <option value="CA">California (CA)</option>
            <option value="FL">Florida (FL)</option>
            <option value="TX">Texas (TX)</option>
            <option value="NY">New York (NY)</option>
            <option value="IL">Illinois (IL)</option>
            <option value="OH">Ohio (OH)</option>
            <option value="PA">Pennsylvania (PA)</option>
          </select>
        </div>

        <div className="scenario-field">
          <label className="scenario-label">
            <Calendar size={13} />
            <span>Date of Loss</span>
          </label>
          <input
            type="date"
            className="scenario-input"
            value={scenario.date_of_loss || ''}
            onChange={(e) => onChange('date_of_loss', e.target.value)}
          />
        </div>

        <div className="scenario-field">
          <label className="scenario-label">
            <AlertTriangle size={13} />
            <span>Claim Type</span>
          </label>
          <select
            className="scenario-select"
            value={scenario.claim_type || ''}
            onChange={(e) => onChange('claim_type', e.target.value)}
          >
            <option value="">Any Claim Type (Optional)</option>
            <option value="water_damage">Water Damage / Burst Pipe</option>
            <option value="fire_smoke">Fire &amp; Smoke Damage</option>
            <option value="wind_hail">Windstorm &amp; Hail</option>
            <option value="theft_vandalism">Theft &amp; Vandalism</option>
            <option value="liability">Personal Liability</option>
            <option value="collapse">Structural Collapse</option>
            <option value="flood">Flood / Surface Water</option>
          </select>
        </div>
      </div>
    </div>
  );
}
