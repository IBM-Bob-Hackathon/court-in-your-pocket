import { useNavigate } from 'react-router-dom';

const SafetyBlockScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="fixed inset-0 z-50 bg-red-600 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-2xl p-8 text-center">
        <div className="text-6xl mb-4">🛑</div>
        <h1 className="text-3xl font-bold text-red-600 mb-4">SAFETY ALERT</h1>
        <p className="text-gray-700 mb-6 text-lg">
          We cannot assist with this type of issue. Please contact appropriate authorities:
        </p>
        
        <div className="space-y-4 mb-8 text-left">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">📞</span>
            <div>
              <p className="font-semibold text-gray-900">National Emergency</p>
              <a href="tel:112" className="text-blue-600 text-xl font-bold">112</a>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">📞</span>
            <div>
              <p className="font-semibold text-gray-900">Women Helpline</p>
              <a href="tel:1091" className="text-blue-600 text-xl font-bold">1091</a>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">📞</span>
            <div>
              <p className="font-semibold text-gray-900">Legal Aid Helpline</p>
              <a href="tel:15100" className="text-blue-600 text-xl font-bold">15100</a>
            </div>
          </div>
        </div>

        <button
          onClick={() => navigate('/')}
          className="w-full bg-gray-900 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
        >
          Exit to Home
        </button>
      </div>
    </div>
  );
};

export default SafetyBlockScreen;

// Made with Bob
