import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import useAppStore from '../store/useAppStore';
import { chatAPI } from '../services/api';
import { jsPDF } from 'jspdf';

const ActionPlanScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sessionId } = useAppStore();
  
  const [actionPlan, setActionPlan] = useState(null);
  const [document, setDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingDoc, setIsGeneratingDoc] = useState(false);
  const [error, setError] = useState(null);
  
  // Get selected option from navigation state
  const selectedOption = location.state?.selectedOption;

  useEffect(() => {
    if (!sessionId) {
      navigate('/welcome', { replace: true });
      return;
    }

    if (!selectedOption) {
      navigate('/rights', { replace: true });
      return;
    }

    generateActionPlan();
  }, [sessionId, selectedOption, navigate]);

  const generateActionPlan = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get session data to extract category and sub_scenario
      const sessionResponse = await fetch(`/api/session/${sessionId}`);
      if (!sessionResponse.ok) {
        throw new Error('Failed to fetch session data');
      }
      const sessionData = await sessionResponse.json();
      
      const category = sessionData.category || 'tenant';
      const subScenario = sessionData.extractedFacts?.issue || 'general_issue';

      // Generate action plan
      const response = await chatAPI.generateActionPlan(
        sessionId,
        category,
        subScenario,
        selectedOption
      );

      setActionPlan(response);
    } catch (err) {
      console.error('Error generating action plan:', err);
      setError(err.message || 'Failed to generate action plan');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateDocument = async () => {
    setIsGeneratingDoc(true);
    setError(null);

    try {
      // Get session data to extract category
      const sessionResponse = await fetch(`/api/session/${sessionId}`);
      if (!sessionResponse.ok) {
        throw new Error('Failed to fetch session data');
      }
      const sessionData = await sessionResponse.json();
      const category = sessionData.category || 'tenant';

      // Generate document with category and option
      const response = await chatAPI.generateDocument(sessionId, category, selectedOption);
      setDocument(response.documentText);
    } catch (err) {
      console.error('Error generating document:', err);
      setError(err.message || 'Failed to generate document');
    } finally {
      setIsGeneratingDoc(false);
    }
  };

  const downloadDocument = () => {
    if (!document) return;
    
    try {
      // Create PDF using jsPDF
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Set font
      pdf.setFont('times', 'normal');
      pdf.setFontSize(12);

      // Add document content
      // Split text into lines that fit the page width
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const maxLineWidth = pageWidth - (margin * 2);
      const lineHeight = 7;
      
      // Split document into lines
      const lines = pdf.splitTextToSize(document, maxLineWidth);
      
      let y = margin;
      
      lines.forEach((line, index) => {
        // Check if we need a new page
        if (y + lineHeight > pageHeight - margin) {
          pdf.addPage();
          y = margin;
        }
        
        pdf.text(line, margin, y);
        y += lineHeight;
      });

      // Save the PDF
      const fileName = `legal-document-${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  const shareViaWhatsApp = () => {
    if (!document) return;
    const text = encodeURIComponent(document);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gold-500 border-t-transparent"></div>
          <p className="text-white mt-4 text-lg">Generating your action plan...</p>
        </div>
      </div>
    );
  }

  if (error && !actionPlan) {
    return (
      <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
        <div className="bg-red-900 border border-red-700 rounded-lg p-6 max-w-md">
          <h2 className="text-red-300 text-xl font-bold mb-2">Error</h2>
          <p className="text-red-200">{error}</p>
          <button
            onClick={() => navigate('/rights')}
            className="mt-4 bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const optionLabels = {
    'A': 'Send Demand Letter',
    'B': 'File Complaint',
    'C': 'Seek Free Legal Aid'
  };

  return (
    <div className="min-h-screen bg-navy-950 text-white">
      <div className="max-w-4xl mx-auto p-4 pb-24">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/rights')}
            className="flex items-center text-gold-500 hover:text-gold-400 mb-4 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Rights
          </button>
          <h1 className="text-2xl md:text-3xl font-bold text-gold-500 mb-2">
            Your Action Plan
          </h1>
          <p className="text-gray-400 text-sm">
            Step-by-step guide for: {optionLabels[selectedOption] || selectedOption}
          </p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-6">
            <p className="text-red-200 text-sm">⚠️ {error}</p>
          </div>
        )}

        {/* Action Plan Steps */}
        {actionPlan?.steps && (
          <div className="space-y-4 mb-6">
            <h2 className="text-xl font-semibold text-gold-500 mb-4">Action Steps</h2>
            {actionPlan.steps.map((step, index) => (
              <div key={index} className="bg-navy-900 rounded-lg border border-navy-800 p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gold-500 text-navy-950 flex items-center justify-center font-bold text-lg mr-4">
                    {step.step_number}
                  </div>
                  <div className="flex-1">
                    <p className="text-white text-base leading-relaxed mb-2">
                      {step.instruction}
                    </p>
                    <div className="flex items-center text-gray-400 text-sm">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Estimated time: {step.time_estimate}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Document Section - Available for all options */}
        <div className="bg-navy-900 rounded-lg border border-navy-800 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gold-500 mb-4">
            {selectedOption === 'A' ? 'Generate Demand Letter' :
             selectedOption === 'B' ? 'Generate Complaint Document' :
             'Legal Aid Information Document'}
          </h2>
          <p className="text-gray-400 text-sm mb-4">
            Generate a customized document based on your action plan and case details.
          </p>
          
          {!document && !isGeneratingDoc && (
            <button
              onClick={handleGenerateDocument}
              className="w-full bg-gold-500 hover:bg-gold-600 text-navy-950 font-semibold py-3 rounded-lg transition-colors flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Generate Document
            </button>
          )}

          {isGeneratingDoc && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gold-500 border-t-transparent mb-4"></div>
              <p className="text-gray-400">Generating your document...</p>
            </div>
          )}

          {document && (
            <div>
              <div className="bg-navy-950 rounded border border-navy-700 p-4 mb-4 max-h-96 overflow-y-auto">
                <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono">
                  {document}
                </pre>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={downloadDocument}
                  className="flex-1 bg-gold-500 hover:bg-gold-600 text-navy-950 font-semibold py-3 rounded-lg transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download Document
                </button>
                <button
                  onClick={shareViaWhatsApp}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                  </svg>
                  Share via WhatsApp
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Next Steps */}
        <div className="bg-navy-900 rounded-lg border border-navy-800 p-6">
          <h2 className="text-xl font-semibold text-gold-500 mb-4">Need More Help?</h2>
          <p className="text-gray-300 mb-4">
            If you need additional assistance or have questions about your action plan, consider consulting with a legal professional.
          </p>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-navy-800 hover:bg-navy-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            Start New Case
          </button>
        </div>
      </div>
    </div>
  );
};

export default ActionPlanScreen;

// Made with Bob
