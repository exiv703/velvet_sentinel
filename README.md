# 🛡️ Velvet Sentinel - NextGen File Monitoring & Recovery

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-green.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Professional-grade file monitoring and recovery system with modern GUI**

Velvet Sentinel is an advanced file monitoring and recovery application designed to protect your important files from accidental deletion. With its sleek dark-themed interface and comprehensive monitoring capabilities, it provides real-time protection for your critical data.

## ✨ Features

### 🔍 **Real-time Monitoring**
- **Multi-folder monitoring** - Monitor multiple directories simultaneously
- **Change detection** - Detect file creation, modification, and deletion
- **Instant notifications** - Get notified about file system changes
- **Background operation** - Runs silently in the background

### 🗑️ **Smart Recovery System**
- **Dual trash system** - Choose between system trash or custom trash
- **Metadata tracking** - Maintain detailed file metadata for recovery
- **Automatic backup** - Create scheduled backups of monitored folders
- **File restoration** - Restore deleted files with original paths

### 🎨 **Modern Interface**
- **Dark theme** - Professional dark interface with green accents
- **Tabbed layout** - Organized interface with dedicated sections
- **Real-time logs** - Live event logging with timestamps
- **Responsive design** - Clean and intuitive user experience

### 🛠️ **Advanced Tools**
- **Disk scanning** - Scan for potentially deleted files
- **Metadata repair** - Check and repair file metadata
- **Log export** - Export detailed activity logs
- **Debug mode** - Advanced debugging capabilities

![settings_tab](https://github.com/user-attachments/assets/83879bd9-bc9a-4e5a-b37b-f6bbeeeacde1)


## 🚀 Quick Start

### Prerequisites
- **Python 3.6 or higher**
- **Windows 10/11**
- **Required libraries**: `customtkinter`, `win10toast`, `send2trash`

### Installation

1. **Clone or download** the repository
2. **Install dependencies**:
   ```bash
   pip install customtkinter win10toast send2trash
   ```
3. **Run the application**:
   ```bash
   python velvet_sentinel.py
   ```
   Or use the provided batch file:
   ```bash
   run.bat
   ```

## 📖 User Guide

### Getting Started

1. **Launch Velvet Sentinel**
   - The application opens with a modern dark interface
   - Main status shows "Computer is protected"

2. **Add Folders to Monitor**
   - Go to the **Monitoring** tab
   - Click **Add** to select folders for monitoring
   - Selected folders appear in the monitored list

3. **Start Monitoring**
   - Click **🟢 Start monitoring** on the main tab
   - Status changes to "Monitoring active"
   - Real-time logs show file system changes

![main_tab](https://github.com/user-attachments/assets/fa1e13ed-3ef2-4bbc-a43c-5d9774c13d1c)


### File Recovery

#### Using System Trash (Default)
- Files deleted normally go to Windows Recycle Bin
- Use **♻️ Restore selected** to restore from Velvet's interface
- Program tracks file metadata for easy recovery

#### Using Custom Trash
- Enable in **Settings** tab
- Files are moved to Velvet's custom trash folder
- Automatic metadata tracking for all deleted files

### Advanced Features

#### Backup System
- **Automatic backups** - Enable scheduled backups
- **Manual backups** - Create backups on demand
- **Backup restoration** - Restore from previous backups

#### Scanning Tools
- **Disk scan** - Search for deleted files across monitored folders
- **Metadata repair** - Fix corrupted file metadata
- **Log export** - Export detailed activity reports

## ⚠️ Important Limitations

### What Velvet Sentinel CAN Recover
- ✅ Files deleted through the application interface
- ✅ Files in Windows Recycle Bin (with manual restoration)
- ✅ Files moved to custom trash folder
- ✅ Files from scheduled backups

### What Velvet Sentinel CANNOT Recover
- ❌ Files permanently deleted from Recycle Bin (Shift+Delete)
- ❌ Files deleted by malware or viruses
- ❌ Files deleted outside the application
- ❌ Files from formatted drives

## 🔧 Configuration

### Settings Tab Options

| Setting | Description | Default |
|---------|-------------|---------|
| **Enable notifications** | Show system notifications | Off |
| **Notify on new files** | Alert when files are created | On |
| **Notify on modifications** | Alert when files are modified | On |
| **Notify on deletions** | Alert when files are deleted | On |
| **Use system trash** | Use Windows Recycle Bin | On |
| **Debug mode** | Enable detailed logging | Off |
| **Auto backup** | Enable automatic backups | Off |

### Customization
- **Backup interval** - Set backup frequency (hours)
- **Notification duration** - Set notification display time
- **Theme colors** - Built-in dark theme with green accents

## 📋 FAQ

### Q: Can Velvet Sentinel recover files deleted by viruses?
**A:** No. Velvet Sentinel can only recover files that were deleted through its interface or are still in the Windows Recycle Bin. Files deleted by malware are typically permanently removed and require professional data recovery tools.

### Q: Does the program slow down my computer?
**A:** No. Velvet Sentinel uses efficient file system monitoring and runs in the background with minimal resource usage. The monitoring interval is set to 1 second to balance responsiveness and performance.

### Q: Can I monitor network drives?
**A:** Yes, you can add network drives to the monitoring list. However, recovery capabilities may be limited depending on network permissions and drive access.

### Q: How do I export my activity logs?
**A:** Use the **📄 Export logs** button on the main tab. This creates a detailed report including statistics, monitored folders, files in trash, and the complete event log.

### Q: What happens if I delete the trash folder?
**A:** The program will automatically recreate the trash folder when needed. However, any files in the deleted trash folder will be permanently lost.

### Q: Can I use Velvet Sentinel on other operating systems?
**A:** Currently, Velvet Sentinel is designed for Windows 10/11. The notification system and some features are Windows-specific.

## 🛡️ Security & Privacy

- **Local operation** - All monitoring and recovery happens locally
- **No data collection** - No personal data is transmitted
- **Secure trash** - Custom trash folder with proper permissions
- **Metadata protection** - File metadata stored securely

## 🐛 Troubleshooting

### Common Issues

**Program won't start**
- Ensure Python 3.6+ is installed
- Install required dependencies: `pip install customtkinter win10toast send2trash`
- Check Windows permissions

**Files not being detected**
- Verify folders exist and are accessible
- Check Windows file system permissions
- Ensure monitoring is active

**Recovery not working**
- Check if files are in Windows Recycle Bin
- Verify custom trash folder exists
- Use metadata repair tool

**Performance issues**
- Reduce number of monitored folders
- Disable debug mode
- Check available disk space

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

Velvet Sentinel is a file monitoring and recovery tool designed for educational and personal use. It is not a replacement for professional data recovery services or backup solutions. The authors are not responsible for any data loss or damage that may occur while using this software.

**Always maintain regular backups of important data using professional backup solutions.**

---

**Made with ❤️ for data protection** 
