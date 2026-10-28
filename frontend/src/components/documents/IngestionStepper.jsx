import React from 'react';
import { FileUp, Sparkles, Layers, Cpu, Database, Check } from 'lucide-react';

export default function IngestionStepper() {
  const steps = [
    {
      number: 1,
      title: 'Load & Extract',
      desc: 'PDF, DOCX, TXT',
      icon: <FileUp size={16} />,
      status: 'complete',
    },
    {
      number: 2,
      title: 'Clean & Normalize',
      desc: 'Header/Footer strip',
      icon: <Sparkles size={16} />,
      status: 'complete',
    },
    {
      number: 3,
      title: 'Token Chunking',
      desc: '400-500 tokens / 15% overlap',
      icon: <Layers size={16} />,
      status: 'complete',
    },
    {
      number: 4,
      title: 'Pinecone Embed',
      desc: 'multilingual-e5-large',
      icon: <Cpu size={16} />,
      status: 'complete',
    },
    {
      number: 5,
      title: 'Vector Upsert',
      desc: '1536-dim metadata indexed',
      icon: <Database size={16} />,
      status: 'complete',
    },
  ];

  return (
    <div className="ingestion-stepper-card">
      <div className="stepper-header">
        <span className="stepper-title">Ingestion Telemetry Pipeline</span>
        <span className="stepper-badge">
          <Check size={12} className="text-emerald" />
          <span>Pipeline Healthy</span>
        </span>
      </div>

      <div className="stepper-row">
        {steps.map((step, idx) => (
          <React.Fragment key={step.number}>
            <div className="stepper-step">
              <div className="step-circle complete">
                <Check size={14} />
              </div>
              <div className="step-content">
                <span className="step-name">{step.title}</span>
                <span className="step-caption">{step.desc}</span>
              </div>
            </div>
            {idx < steps.length - 1 && <div className="step-connector complete"></div>}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

