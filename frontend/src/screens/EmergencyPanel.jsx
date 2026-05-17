const EmergencyPanel = ({ state = 'KA' }) => {
  const stateContacts = {
    KA: { name: 'Karnataka State Legal Services Authority', phone: '080-22862401' },
    MH: { name: 'Maharashtra State Legal Services Authority', phone: '022-22620859' },
    DL: { name: 'Delhi State Legal Services Authority', phone: '011-23385891' }
  };

  const contact = stateContacts[state] || stateContacts.KA;

  return (
    <div className="bg-gradient-to-br from-amber-900/20 to-amber-800/20 border-2 border-amber-500/50 rounded-2xl p-5 shadow-xl shadow-amber-900/30 animate-fade-in">
      <div className="flex items-start gap-4">
        <span className="text-4xl">⚠️</span>
        <div className="flex-1">
          <h3 className="font-bold text-amber-400 mb-3 text-lg">
            This issue requires specialized legal assistance
          </h3>
          <p className="text-slate-300 mb-4">
            Here are free resources that can help you:
          </p>

          <div className="space-y-3">
            <div className="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🏛️</span>
                <p className="font-semibold text-slate-200">National Legal Services Authority (NALSA)</p>
              </div>
              <a href="tel:15100" className="text-amber-400 font-bold text-lg hover:text-amber-300 transition-colors">📞 15100</a>
              <p className="text-sm text-slate-400 mt-1">Toll-free legal aid helpline</p>
            </div>

            <div className="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🏛️</span>
                <p className="font-semibold text-slate-200">{contact.name}</p>
              </div>
              <a href={`tel:${contact.phone}`} className="text-amber-400 font-bold text-lg hover:text-amber-300 transition-colors">
                📞 {contact.phone}
              </a>
            </div>

            <a
              href="https://nalsa.gov.in/legal-aid-clinics"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-900 text-center py-3.5 px-4 rounded-xl font-semibold transition-all duration-200 shadow-lg shadow-amber-500/30 hover:shadow-amber-500/50"
            >
              Find Nearest Legal Aid Center →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmergencyPanel;

// Made with Bob
