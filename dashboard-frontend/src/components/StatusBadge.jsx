import React from 'react';

function StatusBadge({ status }) {
  const getStatusConfig = (status) => {
    switch (status) {
      case 'pending':
        return {
          label: 'Pendente',
          className: 'bg-yellow-100 text-yellow-800'
        };
      case 'in_progress':
        return {
          label: 'Em Atendimento',
          className: 'bg-blue-100 text-blue-800'
        };
      case 'completed':
        return {
          label: 'Finalizada',
          className: 'bg-green-100 text-green-800'
        };
      case 'requires_attention':
        return {
          label: 'Atenção',
          className: 'bg-red-100 text-red-800'
        };
      case 'spam':
        return {
          label: 'Spam',
          className: 'bg-gray-100 text-gray-800'
        };
      default:
        return {
          label: 'Desconhecido',
          className: 'bg-gray-100 text-gray-800'
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${config.className}`}>
      {config.label}
    </span>
  );
}

export default StatusBadge; 