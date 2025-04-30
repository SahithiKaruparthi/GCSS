import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from '../services/api';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const RiskAssessment = () => {
  const { patientId } = useParams();
  const [riskReport, setRiskReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRiskAssessment = async () => {
      try {
        const response = await axios.get(`/patients/${patientId}/risk`);
        setRiskReport(response.data);
      } catch (err) {
        setError(err.response?.data?.msg || 'Error fetching risk assessment');
      } finally {
        setLoading(false);
      }
    };

    fetchRiskAssessment();
  }, [patientId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4" role="alert">
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (!riskReport) {
    return (
      <div className="text-gray-600">No risk assessment available for this patient.</div>
    );
  }

  // Prepare data for the risk factors chart
  const riskFactorsData = {
    labels: ['Genetic Risk', 'Family History Risk', 'Lifestyle Risk'],
    datasets: [
      {
        label: 'Risk Score',
        data: [
          riskReport.genetic_risk || 0,
          riskReport.family_risk || 0,
          riskReport.lifestyle_risk || 0,
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const getRiskColor = (riskLevel) => {
    if (!riskLevel) return 'bg-gray-200';
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'bg-red-500';
      case 'moderate':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-200';
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Risk Assessment</h1>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className={`h-2 w-full ${getRiskColor(riskReport.risk_level)}`}></div>
        <div className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold mb-1">Risk Level: {riskReport.risk_level}</h2>
              <p className="text-gray-600 text-sm mb-4">
                Assessment Date: {new Date(riskReport.assessment_date).toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <span className={`inline-block px-3 py-1 rounded-full text-white font-bold ${getRiskColor(riskReport.risk_level)}`}>
                {riskReport.risk_level}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Risk Score</h3>
              <div className="bg-gray-100 rounded-lg p-4">
                <p className="text-3xl font-bold text-blue-600">
                  {riskReport.risk_score}
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Recommendations</h3>
              <div className="bg-gray-100 rounded-lg p-4">
                <p className="text-gray-700">
                  {riskReport.recommendations || 'No specific recommendations available'}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Risk Factors Breakdown</h3>
            <div className="h-64">
              <Bar
                data={riskFactorsData}
                options={{
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Contributing Factors</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-gray-100 rounded-lg p-4">
                <h4 className="font-medium">Genetic Tests</h4>
                <p className="text-sm text-gray-600">
                  {riskReport.genetic_tests_count || 0} tests
                </p>
              </div>
              <div className="bg-gray-100 rounded-lg p-4">
                <h4 className="font-medium">Family History</h4>
                <p className="text-sm text-gray-600">
                  {riskReport.family_history_count || 0} entries
                </p>
              </div>
              <div className="bg-gray-100 rounded-lg p-4">
                <h4 className="font-medium">Lifestyle Factors</h4>
                <p className="text-sm text-gray-600">
                  {riskReport.lifestyle_factors_count || 0} factors
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;