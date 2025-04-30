import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const PatientDetail = () => {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await axios.get(`/api/patients/${patientId}`);
        setPatient(response.data);
      } catch (error) {
        console.error('Error fetching patient:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPatient();
  }, [patientId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-red-500">Patient not found</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">
                {patient.patient.first_name} {patient.patient.last_name}
              </h1>
              <p className="text-gray-600">
                Date of Birth: {new Date(patient.patient.date_of_birth).toLocaleDateString()} | 
                Gender: {patient.patient.gender}
              </p>
            </div>
            <Link
              to={`/patients/${patientId}/risk-assessment`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
            >
              View Risk Assessment
            </Link>
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex space-x-4 border-b mb-4">
            <button
              className={`px-4 py-2 ${activeTab === 'overview' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`px-4 py-2 ${activeTab === 'genetic-tests' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('genetic-tests')}
            >
              Genetic Tests
            </button>
            <button
              className={`px-4 py-2 ${activeTab === 'family-history' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('family-history')}
            >
              Family History
            </button>
            <button
              className={`px-4 py-2 ${activeTab === 'lifestyle' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('lifestyle')}
            >
              Lifestyle Factors
            </button>
          </div>
          
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-xl font-bold mb-4">Latest Risk Assessment</h2>
                {patient.risk_reports.length > 0 ? (
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold">
                        {patient.risk_reports[0].risk_level} Risk
                      </h3>
                      <p className="text-sm text-gray-600">
                        {new Date(patient.risk_reports[0].assessment_date).toLocaleDateString()}
                      </p>
                    </div>
                    <p className="text-gray-700">
                      {patient.risk_reports[0].recommendations}
                    </p>
                  </div>
                ) : (
                  <p className="text-gray-600">No risk assessments available</p>
                )}
              </div>
              
              <div>
                <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-600">Genetic Tests</h3>
                    <p className="text-2xl font-bold">
                      {patient.genetic_tests.length}
                    </p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-600">Family Members</h3>
                    <p className="text-2xl font-bold">
                      {patient.family_history.length}
                    </p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-600">Lifestyle Factors</h3>
                    <p className="text-2xl font-bold">
                      {patient.lifestyle_factors.length}
                    </p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-600">Risk Reports</h3>
                    <p className="text-2xl font-bold">
                      {patient.risk_reports.length}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'genetic-tests' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Genetic Tests</h2>
              {patient.genetic_tests.length > 0 ? (
                <div className="space-y-4">
                  {patient.genetic_tests.map(test => (
                    <div key={test.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-medium">{test.gene}</h3>
                          <p className="text-sm text-gray-600">{test.mutation}</p>
                        </div>
                        <span className={`px-2 py-1 text-sm rounded-full ${getRiskColor(test.risk_level)}`}>
                          {test.risk_level}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        Test Date: {new Date(test.test_date).toLocaleDateString()}
                      </p>
                      {test.result && (
                        <p className="text-sm text-gray-600 mt-1">
                          Result: {test.result}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No genetic tests available</p>
              )}
            </div>
          )}
          
          {activeTab === 'family-history' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Family History</h2>
              {patient.family_history.length > 0 ? (
                <div className="space-y-4">
                  {patient.family_history.map(history => (
                    <div key={history.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-medium">{history.relation}</h3>
                          <p className="text-sm text-gray-600">{history.disease}</p>
                        </div>
                        <p className="text-sm text-gray-600">
                          Age: {history.onset_age}
                        </p>
                      </div>
                      {history.notes && (
                        <p className="text-sm text-gray-600 mt-1">
                          Notes: {history.notes}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No family history recorded</p>
              )}
            </div>
          )}
          
          {activeTab === 'lifestyle' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Lifestyle Factors</h2>
              {patient.lifestyle_factors.length > 0 ? (
                <div className="space-y-4">
                  {patient.lifestyle_factors.map(factor => (
                    <div key={factor.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-medium">{factor.factor_type}</h3>
                          <p className="text-sm text-gray-600">{factor.value}</p>
                        </div>
                      </div>
                      {factor.notes && (
                        <p className="text-sm text-gray-600 mt-1">
                          Notes: {factor.notes}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No lifestyle factors recorded</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const getRiskColor = (riskLevel) => {
  if (!riskLevel) return 'bg-gray-200 text-gray-800';
  
  switch (riskLevel.toLowerCase()) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'moderate':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-200 text-gray-800';
  }
};

export default PatientDetail;