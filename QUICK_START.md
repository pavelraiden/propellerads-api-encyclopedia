# 🚀 Quick Start Guide

## One-Click Setup & Launch

### 1. 📥 Download & Setup
```bash
git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia
python3 setup.py
```

### 2. 🔑 Configure API Keys
Edit `.env` file and add your keys:
```
MainAPI=your_propellerads_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
```

**Get API Keys:**
- 🎯 PropellerAds: https://ssp.propellerads.com/
- 🤖 Claude: https://console.anthropic.com/

### 3. 🖱️ Launch Application

**🎯 Recommended (Unified Interface):**
```bash
python3 simple_app.py
```

**🖱️ One-Click Launchers:**
- **Windows:** Double-click `launch_app.bat`  
- **macOS/Linux:** Double-click `launch_app.sh` or run `./launch_app.sh`  
- **Any OS:** Run `python3 launch_app.py`

**📚 Advanced Interface:**
```bash
cd web_interface && python3 app.py
```

### 4. 🌐 Use the App

**🎯 Unified Dashboard (Recommended):**
- **URL:** Shown in console when app starts (usually http://127.0.0.1:5000)
- **Everything in one place** - Dashboard, Chat, Campaigns, Statistics
- **Claude AI Chat** built-in and working
- **Real-time updates** automatic

## 💡 Features
- ✅ **One-click launch** - No command line needed
- ✅ **Auto-setup** - Installs dependencies automatically  
- ✅ **Web interface** - Modern dashboard
- ✅ **AI assistant** - Natural language commands
- ✅ **185 tests** - Production ready

## 🆘 Troubleshooting
- **Python not found:** Install Python 3.9+ from https://python.org
- **API errors:** Check your API keys in `.env` file
- **Port busy:** Change `WEB_PORT=5001` in `.env` file

## 📞 Support
- 📖 Full docs: See `README.md`
- 🐛 Issues: GitHub Issues
- 💬 Questions: Check `USER_GUIDE_FOR_NON_DEVELOPERS.md`
