# **MyScheme App**

**Citizen-Centric Awareness Platform for Government Schemes**

A comprehensive Flutter-based mobile application designed to help Indian citizens easily discover, understand, and access government welfare schemes using modern technologies like AI, location services, and multilingual support.

---

## 📌 Project Overview

The **MyScheme App** addresses key challenges such as lack of awareness, language barriers, and complex application processes associated with government welfare schemes.
The application was **tested within the Nambur community, Guntur District, Andhra Pradesh**, and demonstrated improved accessibility and awareness of welfare programs.

---

## 🚀 Features

### ✨ Core Features

* **Government Schemes Database** – Browse and explore various Indian government schemes
* **AI-Powered Chatbot** – Context-aware chatbot powered by **Google Gemini AI**
* **Smart Search & Filters** – Search schemes by keywords and categories
* **Location-Based Weather Updates** – Real-time weather information using GPS
* **Text-to-Speech (TTS)** – Accessibility feature to read scheme details aloud
* **Favorites / Bookmarks** – Save important schemes for later reference
* **User Profile** – Manage preferences and personal settings
* **Multi-language Support** – Supports multiple Indian languages
* **Modern UI** – Material Design 3 with smooth animations

---

### 🔧 Technical Features

* Cross-platform support (**Android, iOS, Web**)
* Provider-based state management
* API integration with retry mechanisms
* Local persistence using **SharedPreferences**
* Responsive and adaptive UI
* Robust error handling and graceful fallbacks
* CORS proxy support for web platform

---

## 🛠️ Tech Stack

* **Framework**: Flutter
* **Language**: Dart
* **State Management**: Provider
* **AI Integration**: Google Gemini (`gemini-1.5-flash`)
* **APIs**: OpenWeatherMap, Government Schemes API
* **Storage**: SharedPreferences

---

## 📂 Project Structure

```
lib/
├── main.dart
├── models/
│   ├── scheme.dart
│   ├── weather_model.dart
│   └── chat_message.dart
├── providers/
│   ├── scheme_provider.dart
│   ├── weather_provider.dart
│   ├── location_provider.dart
│   └── chat_provider.dart
├── screens/
│   ├── splash_screen.dart
│   ├── home_screen.dart
│   ├── scheme_list_screen.dart
│   ├── scheme_detail_screen.dart
│   ├── chat_screen.dart
│   ├── weather_detail_screen.dart
│   └── profile_screen.dart
├── services/
│   ├── api_service.dart
│   ├── api_service_mobile.dart
│   ├── api_service_web.dart
│   ├── weather_service.dart
│   ├── chat_service.dart
│   ├── location_service.dart
│   ├── tts_service.dart
│   └── preferences_service.dart
├── widgets/
│   ├── scheme_card.dart
│   ├── weather_summary.dart
│   └── bottom_nav_bar.dart
└── utils/
    ├── constants.dart
    └── mock_data.dart
```

---

## 📦 Dependencies

* `provider`
* `google_generative_ai`
* `http`
* `geolocator`
* `flutter_tts`
* `shared_preferences`
* `url_launcher`
* `google_fonts`

---

## ⚙️ Getting Started

### Prerequisites

* Flutter SDK **>= 3.4.3**
* Dart SDK **>= 3.4.3**
* Android Studio / VS Code
* Active internet connection

---

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd myscheme_app
```

#### 2️⃣ Install Dependencies

```bash
flutter pub get
```

#### 3️⃣ Configure API Keys

Edit `lib/utils/constants.dart`:

```dart
const String weatherApiKey = "YOUR_WEATHER_API_KEY";
const String geminiApiKey = "YOUR_GEMINI_API_KEY";
```

🔐 **Security Note**:
Do **not** commit API keys. Use environment variables or secure storage in production.

---

#### 4️⃣ Run the Application

```bash
flutter run
```

---

## 📱 Platform-Specific Setup

### Android

* Minimum SDK: 21
* No additional setup required

### iOS

Add location permission in `Info.plist`:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to provide weather updates</string>
```

### Web

```bash
flutter run -d chrome
```

CORS proxies are preconfigured for API calls.

---

## 📊 Usage Guide

### Browse Schemes

* View recommended schemes on the home screen
* Search and filter schemes by category

### AI Chatbot

* Ask about eligibility, documents, deadlines, and benefits
* Context-aware responses based on available schemes

### Favorites

* Bookmark schemes
* View saved schemes via profile

### Profile Customization

* Language preferences
* Notification settings
* User information

---

## ✅ Improvements Implemented

### Security

* API key usage warnings
* Recommended environment-based storage

### Functionality

* Gemini AI updated to `gemini-1.5-flash`
* Search and category filtering
* Context-aware chatbot
* Local storage integration
* URL launcher for official scheme links

### UX/UI

* Improved loading states
* Better error handling
* Enhanced scheme cards
* Clear empty states

---

## ⚠️ Known Limitations

* API keys are currently hardcoded
* No authentication system
* Limited offline functionality
* No push notifications
* No dedicated favorites screen

---

## 🔮 Future Enhancements

* User authentication (Firebase / OAuth)
* Push notifications
* Offline mode with local database
* Advanced eligibility filters (age, income, state)
* Scheme application tracking
* Dark mode
* Voice-enabled navigation
* Personalized scheme recommendations

---

## 🤝 Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

---

## 🏫 Academic Details

* **Institution**: Vasireddy Venkatadri Institute of Technology (VVIT), Nambur
* **Duration**: July 2025 – November 2025
* **Project Guide**:
  **Dr. T. Kameswara Rao**
  Professor, CSE (AI & ML), VVIT
* **Project Coordinator**:
  **Mohammad Sayeed**
  Assistant Professor, CSE (AI & ML), VVIT

---

## 🧠 Skills Gained

* Mobile Application Development
* Flutter & Dart
* API Integration
* AI Chatbot Development
* UI/UX Design

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 📞 Support

For support, open an issue in the repository or contact:
📧 **[support@myscheme.gov.in](mailto:support@myscheme.gov.in)**

---

## 🙏 Acknowledgments

* MyScheme.gov.in
* OpenWeatherMap
* Google Gemini AI
* Flutter Team

---

**Version**: 1.1.0
**Last Updated**: JUNE 2026

Project maintained by Adhimulam Yamuna Tara.

---
