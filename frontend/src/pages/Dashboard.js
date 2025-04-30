import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { currentUser } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [geneMutations, setGeneMutations] = useState([]);
  const [diseaseDistribution, setDiseaseDistribution] = useState([]);
  const [patientCount, setPatientCount] = useState(0);
  const [patientData, setPatientData] = useState(null);
  const [latestRisk, setLatestRisk] = useState(null);
  
  const isCounselor = currentUser?.role === 'counselor' || currentUser?.role === 'admin';
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        if (isCounselor) {
          // Fetch data for counselor dashboard
          const [riskRes, geneRes, diseaseRes, patientsRes] = await Promise.all([
            axios.get('/stats/risk-distribution'),
            axios.get('/stats/gene-mutation-counts'),
            axios.get('/stats/disease-distribution'),
            axios.get('/patients')
          ]);
          
          setRiskDistribution(riskRes.data);
          setGeneMutations(geneRes.data);
          setDiseaseDistribution(diseaseRes.data);
          setPatientCount(patientsRes.data.length);
        } else {
          // Fetch data for patient dashboard
          const patientId = currentUser.id;
          const [patientRes, riskRes] = await Promise.all([
            axios.get(`/patients/${patientId}`),
            axios.get(`/patients/${patientId}/risk`)
          ]);
          
          setPatientData(patientRes.data);
          setLatestRisk(riskRes.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (currentUser) {
      fetchDashboardData();
    }
  }, [currentUser, isCounselor]);
  
  // Prepare chart data for risk distribution
  const riskChartData = {
    labels: riskDistribution.map(item => item.risk_level),
    datasets: [
      {
        label: 'Risk Distribution',
        data: riskDistribution.map(item => item.count),
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 99, 132, 0.6)',
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Prepare chart data for gene mutations
  const geneChartData = {
    labels: geneMutations.map(item => item.gene),
    datasets: [
      {
        label: 'Gene Mutations',
        data: geneMutations.map(item => item.count),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };
  
  // Prepare chart data for disease distribution
  const diseaseChartData = {
    labels: diseaseDistribution.map(item => disease => 
      disease.length > 15 ? `${disease.substring(0, 15)}...` : disease),
    datasets: [
      {
        label: 'Disease Distribution',
        data: diseaseDistribution.map(item => item.count),
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
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
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      {isCounselor ? (
        // Counselor Dashboard
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Total Patients</h3>
              <p className="text-3xl font-bold text-blue-600">{patientCount}</p>
              <Link to="/patients" className="text-blue-500 hover:underline text-sm mt-2 inline-block">
                View All Patients
              </Link>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Risk Overview</h3>
              <div className="flex space-x-2 mt-4">
                {riskDistribution.map(risk => (
                  <div key={risk.risk_level} className="flex-1 text-center">
                    <div className={`h-2 w-full mb-1 rounded ${getRiskColor(risk.risk_level)}`}></div>
                    <p className="text-sm font-medium">{risk.risk_level}</p>
                    <p className="text-lg font-bold">{risk.count}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
              <div className="space-y-2 mt-4">
                <Link 
                  to="/patients" 
                  className="block w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded text-center"
                >
                  View Patients
                </Link>
                <button 
                  className="block w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white rounded text-center"
                  onClick={() => window.open('/api/stats/export/report', '_blank')}
                >
                  Generate Report
                </button>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
              <div className="h-64">
                <Pie data={riskChartData} options={{ maintainAspectRatio: false }} />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Top Gene Mutations</h3>
              <div className="h-64">
                <Bar 
                  data={geneChartData} 
                  options={{ 
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }} 
                />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Common Diseases</h3>
              <div className="h-64">
                <Bar 
                  data={diseaseChartData} 
                  options={{ 
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }} 
                />
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Patient Dashboard
        <div>
          <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-6">
            <div className={`h-2 w-full ${getRiskColor(latestRisk?.risk_level)}`}></div>
            <div className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold mb-1">Your Risk Assessment</h2>
                  <p className="text-gray-600 text-sm mb-4">
                    Last updated: {new Date(latestRisk?.assessment_date).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                                    <span className={`inline-block px-3 py-1 rounded-full text-white font-bold ${getRiskColor(latestRisk?.risk_level)}`}>
                    {latestRisk?.risk_level || 'Not Assessed'}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Risk Score</h3>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <p className="text-3xl font-bold text-blue-600">
                      {latestRisk?.risk_score || 'N/A'}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2">Recommendations</h3>
                  <div className="bg-gray-100 rounded-lg p-4">
                    <p className="text-gray-700">
                      {latestRisk?.recommendations || 'No specific recommendations available'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <Link 
                  to={`/patients/${currentUser.id}/risk-assessment`} 
                  className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                >
                  View Detailed Risk Assessment
                </Link>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Your Genetic Tests</h3>
              {patientData?.genetic_tests?.length > 0 ? (
                <div className="space-y-4">
                  {patientData.genetic_tests.slice(0, 3).map(test => (
                    <div key={test.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex justify-between items-center">
                        <div>
                          <h4 className="font-medium">{test.gene}</h4>
                          <p className="text-sm text-gray-600">{test.mutation}</p>
                        </div>
                        <span className={`px-2 py-1 text-sm rounded-full ${getRiskColor(test.risk_level)}`}>
                          {test.risk_level}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        Test Date: {new Date(test.test_date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No genetic tests available</p>
              )}
              <div className="mt-4">
                <Link 
                  to={`/patients/${currentUser.id}`} 
                  className="text-blue-500 hover:underline"
                >
                  View All Genetic Tests
                </Link>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Family History</h3>
              {patientData?.family_history?.length > 0 ? (
                <div className="space-y-4">
                  {patientData.family_history.slice(0, 3).map(history => (
                    <div key={history.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex justify-between items-center">
                        <div>
                          <h4 className="font-medium">{history.relation}</h4>
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
              <div className="mt-4">
                <Link 
                  to={`/patients/${currentUser.id}`} 
                  className="text-blue-500 hover:underline"
                >
                  View Full Family History
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;