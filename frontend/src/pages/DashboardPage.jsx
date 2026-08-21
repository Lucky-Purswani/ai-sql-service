import React, { useState } from 'react';
import ConnectionList from '../components/connections/ConnectionList';
import ConnectionForm from '../components/connections/ConnectionForm';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import { useConnections } from '../hooks/useConnections';

export default function DashboardPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    connections, isLoading, error, processingId, processingType, 
    addConnection, deleteConnection, syncConnection 
  } = useConnections();

  const handleAddConnection = async (formData) => {
    setIsSubmitting(true);
    setFormError('');
    try {
      await addConnection(formData);
      setIsModalOpen(false);
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to add connection');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="dashboard-title">Your Databases</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          + Add Connection
        </Button>
      </header>

      <ConnectionList 
        connections={connections} 
        onDelete={deleteConnection}
        onSync={syncConnection}
        processingId={processingId}
        processingType={processingType}
      />

      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        title="Connect Database"
      >
        <ConnectionForm 
          onSubmit={handleAddConnection}
          isLoading={isSubmitting}
          error={formError}
        />
      </Modal>
    </div>
  );
}
