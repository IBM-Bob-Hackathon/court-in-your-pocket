import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../store/useAppStore';

// Constants
const MS_PER_MONTH = 1000 * 60 * 60 * 24 * 30;
const VERIFICATION_RECENT_THRESHOLD = 3; // months
const VERIFICATION_WARNING_THRESHOLD = 6; // months

const RightsScreen = () => {
  const navigate = useNavigate();
  const { sessionId, language } = useAppStore();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);
  const [summaryExpanded, setSummaryExpanded] = useState(true);
  const [expandedRights, setExpandedRights] = useState({});

  useEffect(() => {
    const fetchRights = async () => {
      if (!sessionId) {
        setError('No session found. Please start from the beginning.');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('/api/legal/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ sessionId, language }),
        });

        if (!response.ok) {
          throw new Error('Failed to analyze legal situation');
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRights();
  }, [sessionId, language]);

  const toggleRightExpansion = (index) => {
    setExpandedRights(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleOptionSelect = (optionId) => {
    setSelectedOption(optionId);
  };

  const handleBuildActionPlan = () => {
    if (selectedOption) {
      navigate('/action', { state: { selectedOption } });
    }
  };

  const getConfidenceDots = (score) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={i}
        className={`inline-block w-2 h-2 rounded-full mx-0.5 ${
          i < score ? 'bg-green-500' : 'bg-gray-600'
        }`}
      />
    ));
  };

  const getVerificationBadge = (dateString) => {
    const lastVerified = new Date(dateString);
    
    // Validate date
    if (isNaN(lastVerified.getTime())) {
      return (
        <span className="text-xs px-2 py-1 rounded bg-gray-900 text-gray-400">
          Date unavailable
        </span>
      );
    }
    
    const now = new Date();
    const monthsDiff = (now - lastVerified) / MS_PER_MONTH;

    let bgColor, textColor, label;
    if (monthsDiff < VERIFICATION_RECENT_THRESHOLD) {
      bgColor = 'bg-green-900';
      textColor = 'text-green-300';
      label = 'Recently verified';
    } else if (monthsDiff < VERIFICATION_WARNING_THRESHOLD) {
      bgColor = 'bg-amber-900';
      textColor = 'text-amber-300';
      label = 'Verify for recent changes';
    } else {
      bgColor = 'bg-red-900';
      textColor = 'text-red-300';
      label = 'Confirm with official source';
    }

    return (
      <span className={`text-xs px-2 py-1 rounded ${bgColor} ${textColor}`}>
        {label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gold-500 border-t-transparent"></div>
          <p className="text-white mt-4 text-lg">Analyzing your legal situation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
        <div className="bg-red-900 border border-red-700 rounded-lg p-6 max-w-md">
          <h2 className="text-red-300 text-xl font-bold mb-2">Error</h2>
          <p className="text-red-200">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Handle out-of-scope response
  if (data?.outOfScope) {
    return (
      <div className="min-h-screen bg-navy-950 text-white">
        <div className="max-w-4xl mx-auto p-4">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl md:text-3xl font-bold text-gold-500 mb-2">
              Out of Scope
            </h1>
            <p className="text-gray-400 text-sm">
              We're here to help you find the right resources
            </p>
          </div>

          {/* Message Card */}
          <div className="bg-navy-900 rounded-lg p-6 mb-6 border border-navy-800">
            <p className="text-white text-lg leading-relaxed">
              {data.message}
            </p>
          </div>

          {/* Legal Aid Contacts */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gold-500 mb-4">
              Free Legal Aid Services
            </h2>
            <div className="space-y-4">
              {data.legalAid?.map((contact, index) => (
                <div key={index} className="bg-navy-900 rounded-lg p-5 border border-navy-800">
                  <h3 className="text-white font-semibold text-lg mb-2">
                    {contact.name}
                  </h3>
                  <p className="text-gray-400 text-sm mb-3">
                    {contact.description}
                  </p>
                  <div className="space-y-2">
                    {contact.phone && (
                      <div className="flex items-center text-gray-300">
                        <svg className="w-5 h-5 mr-2 text-gold-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                        <span>{contact.phone}</span>
                      </div>
                    )}
                    {contact.website && (
                      <a
                        href={contact.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-gold-500 hover:text-gold-400 transition-colors"
                      >
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                        <span>Visit Website</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Back Button */}
          <button
            onClick={() => navigate('/')}
            className="w-full bg-gold-500 hover:bg-gold-600 text-navy-950 font-semibold py-4 rounded-lg transition-colors"
          >
            Start Over
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-navy-950 text-white">
      <div className="max-w-4xl mx-auto p-4 pb-24">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-gold-500 mb-2">
            Your Legal Rights
          </h1>
          <p className="text-gray-400 text-sm">
            Based on your situation and applicable Indian laws
          </p>
        </div>

        {/* Deadline Warning Banner */}
        {data?.deadline && (
          <div className="bg-amber-900 border-l-4 border-amber-500 p-4 mb-6 rounded">
            <div className="flex items-center">
              <svg className="w-6 h-6 text-amber-300 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-amber-100 font-semibold">Time-Sensitive Action Required</p>
                <p className="text-amber-200 text-sm">You have approximately {data.deadline} days to act</p>
              </div>
            </div>
          </div>
        )}

        {/* Situation Summary Card */}
        <div className="bg-navy-900 rounded-lg mb-6 overflow-hidden border border-navy-800">
          <button
            onClick={() => setSummaryExpanded(!summaryExpanded)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-navy-800 transition-colors"
          >
            <h2 className="text-lg font-semibold text-gold-500">Situation Summary</h2>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${summaryExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {summaryExpanded && (
            <div className="px-6 pb-4 text-gray-300">
              <p className="text-sm leading-relaxed">
                Based on the information you provided, we've identified the relevant laws and your rights. 
                Review each finding below to understand your legal position.
              </p>
            </div>
          )}
        </div>

        {/* Rights Cards */}
        <div className="space-y-4 mb-6">
          {data?.rights?.map((right, index) => (
            <div key={index} className="bg-navy-900 rounded-lg border border-navy-800 overflow-hidden">
              <div className="p-6">
                {/* Law Name and Section */}
                <div className="mb-3">
                  <h3 className="text-gold-500 font-semibold text-lg mb-1">
                    {right.law_name}
                  </h3>
                  <p className="text-gray-500 text-sm">{right.section}</p>
                </div>

                {/* Plain English Explanation */}
                <p className="text-white font-medium text-base mb-4 leading-relaxed">
                  {right.plain_english}
                </p>

                {/* Badges Row */}
                <div className="flex flex-wrap items-center gap-3 mb-4">
                  {/* Confidence Badge */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Confidence:</span>
                    <div className="flex items-center">
                      {getConfidenceDots(right.confidence)}
                    </div>
                  </div>

                  {/* Verification Badge */}
                  {right.last_verified && getVerificationBadge(right.last_verified)}
                </div>

                {/* Expandable Section */}
                <div className="border-t border-navy-800 pt-4">
                  <button
                    onClick={() => toggleRightExpansion(index)}
                    className="flex items-center text-gold-500 hover:text-gold-400 transition-colors text-sm font-medium"
                  >
                    <span>See original law text</span>
                    <svg
                      className={`w-4 h-4 ml-1 transition-transform ${expandedRights[index] ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {expandedRights[index] && (
                    <div className="mt-4 space-y-3">
                      {/* Exact Quote */}
                      <div className="bg-navy-950 p-4 rounded border-l-4 border-gold-500">
                        <p className="text-gray-300 text-sm italic leading-relaxed">
                          "{right.exact_quote}"
                        </p>
                      </div>

                      {/* Source Link */}
                      {right.source_url && (
                        <a
                          href={right.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-gold-500 hover:text-gold-400 text-sm transition-colors"
                        >
                          <span>View official source</span>
                          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Overall Confidence */}
        {data?.confidence && (
          <div className="bg-navy-900 rounded-lg p-4 mb-6 border border-navy-800">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-sm">Overall Analysis Confidence:</span>
              <div className="flex items-center gap-2">
                {getConfidenceDots(data.confidence)}
                <span className="text-white text-sm ml-2">{data.confidence}/5</span>
              </div>
            </div>
          </div>
        )}

        {/* Options Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gold-500 mb-4">Choose Your Next Step</h2>
          <div className="space-y-3">
            {data?.options?.map((option) => (
              <button
                key={option.id}
                onClick={() => handleOptionSelect(option.id)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedOption === option.id
                    ? 'border-gold-500 bg-gold-500 bg-opacity-10'
                    : 'border-navy-800 bg-navy-900 hover:border-navy-700'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-3 flex-shrink-0 ${
                    selectedOption === option.id
                      ? 'border-gold-500 bg-gold-500'
                      : 'border-gray-500'
                  }`}>
                    {selectedOption === option.id && (
                      <svg className="w-4 h-4 text-navy-950" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <span className="font-medium text-white">{option.id}.</span>
                    <span className="text-white ml-2">{option.label}</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <div className="fixed bottom-0 left-0 right-0 bg-navy-950 border-t border-navy-800 p-4">
          <div className="max-w-4xl mx-auto">
            <button
              onClick={handleBuildActionPlan}
              disabled={!selectedOption}
              className={`w-full py-4 rounded-lg font-semibold text-lg transition-all ${
                selectedOption
                  ? 'bg-gold-500 hover:bg-gold-600 text-navy-950 shadow-lg shadow-gold-500/50'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              Build My Action Plan
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RightsScreen;

// Made with Bob
