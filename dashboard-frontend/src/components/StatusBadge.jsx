import React from 'react';

function StatusBadge({ status }) {
  const getStatusConfig = (status) => {
    switch (status) {
      // Estados do chatbot
      case 'inicio':
        return {
          label: 'Início',
          className: 'bg-green-100 text-green-800'
        };
      case 'menu_principal':
        return {
          label: 'Menu',
          className: 'bg-blue-100 text-blue-800'
        };
      case 'aguardando_cpf':
        return {
          label: 'CPF',
          className: 'bg-yellow-100 text-yellow-800'
        };
      case 'escolhendo_data':
        return {
          label: 'Data',
          className: 'bg-purple-100 text-purple-800'
        };
      case 'escolhendo_horario':
        return {
          label: 'Horário',
          className: 'bg-indigo-100 text-indigo-800'
        };
      case 'confirmando_agendamento':
        return {
          label: 'Confirmar',
          className: 'bg-orange-100 text-orange-800'
        };
      case 'visualizando_agendamentos':
        return {
          label: 'Visualizar',
          className: 'bg-cyan-100 text-cyan-800'
        };
      case 'cancelando_consulta':
        return {
          label: 'Cancelar',
          className: 'bg-red-100 text-red-800'
        };
      case 'lista_espera':
        return {
          label: 'Lista Espera',
          className: 'bg-pink-100 text-pink-800'
        };
      
      // Estados antigos (fallback)
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
          label: status || 'Desconhecido',
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