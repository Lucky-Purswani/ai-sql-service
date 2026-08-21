import React, { useState } from 'react';
import Input from '../common/Input';
import Button from '../common/Button';

export default function ConnectionForm({ onSubmit, isLoading, error }) {
  const [formData, setFormData] = useState({ nickname: '', db_url: '' });
  const [localErrors, setLocalErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!formData.nickname.trim()) newErrors.nickname = 'Nickname is required';
    if (!formData.db_url.trim()) newErrors.db_url = 'Connection URL is required';
    else if (!formData.db_url.startsWith('postgresql://')) {
      newErrors.db_url = 'URL must start with postgresql://';
    }
    
    setLocalErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (localErrors[name]) {
      setLocalErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <form className="connection-form" onSubmit={handleSubmit} noValidate>
      {error && <div className="alert-error">{error}</div>}
      
      <Input
        label="Nickname"
        name="nickname"
        value={formData.nickname}
        onChange={handleChange}
        error={localErrors.nickname}
        placeholder="e.g. Production DB"
      />
      
      <Input
        label="PostgreSQL Connection URL"
        name="db_url"
        type="password" // hide URL since it contains password
        value={formData.db_url}
        onChange={handleChange}
        error={localErrors.db_url}
        placeholder="postgresql://user:password@host:port/dbname"
      />

      <div className="connection-form-actions">
        <Button type="submit" fullWidth isLoading={isLoading}>
          Connect & Scan Database
        </Button>
      </div>
      
      <p className="connection-form-help">
        We will connect to your database, read your schema (table names and column names), 
        and store it in our secure AI vector store. We never read your actual table data.
      </p>
    </form>
  );
}
