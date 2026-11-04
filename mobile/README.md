# AgroLens mobile app

AgroLens is a phone-first Flutter app for photographing crop leaves, adding a
consented farm location required for each scan, and reviewing a crop-health
result. Android asks the user to approve location access after the location
button is tapped; permission is never auto-approved. If GPS is disabled or
permission is blocked, the app offers the relevant device settings. GPS fixes
can take up to 60 seconds. The interface is available in English, Hindi,
Telugu, Tamil, and Kannada.

## Crop coverage

The plant field accepts any crop or plant name. The current demo does **not**
perform image recognition: it generates simulated examples for tomato, potato,
corn, bell pepper, and rice only, and reports unsupported crops instead of
silently substituting tomato. There is no trained TensorFlow Lite model in
this repository yet. Detecting additional plants requires training and
validating a model with representative images and labels for those species and
conditions.

## Run on a phone

Open this directory in Android Studio or Xcode and run the Flutter project on a
connected Android or iOS device. The native `android/` and `ios/` projects are
included. Android builds require the Android SDK; iOS builds require macOS and
Xcode.

To build an Android APK:

```shell
flutter pub get
flutter build apk --release --split-per-abi
```

The split release build creates smaller APKs for `arm64-v8a`, `armeabi-v7a`,
and `x86_64` devices. Use the APK matching the target device; a universal debug
APK is much larger and is intended for development, not distribution.

For browser preview only:

```shell
flutter run -d chrome
```

## Authentication

Login and registration currently use `LocalAuthService`; accounts and the
signed-in session are stored on-device with `SharedPreferences`. Passwords are
salted and hashed. This is development/testing authentication only, not a
production security boundary. No bearer tokens or authentication API calls are
made. Password recovery is unavailable for locally stored accounts. The UI
depends on the `AuthService` interface so a real backend implementation can be
added later without changing the screens.

## Agriculture information features

The agriculture hub adds weather, schemes, news, mandi prices, and local scan
history without changing the existing scan screen. `AppConfig.useMockApi`
defaults to `true`; the clearly labeled development sample responses are not
live weather, government scheme, news, or market information. Set it to
`false` to use `HttpAgricultureDataService` at `AppConfig.backendBaseUrl`.
The shared project specification currently defines scan endpoints only, so the
backend must implement these feature endpoints before using live mode:

| Method and path | Query parameters | Response |
| --- | --- | --- |
| `GET /weather` | `location` | Weather object with optional `forecast` list |
| `GET /schemes` | optional `state`, `category` | Item list or `{ "items": [...] }` |
| `GET /news` | optional `category` | Item list or `{ "items": [...] }` |
| `GET /market/prices` | `commodity`, optional `state`, `district`, `market` | Item list or `{ "items": [...] }` |
| `GET /market/history` | `commodity`, optional `market`, `days` | Item list or `{ "items": [...] }` |
| `GET /market/forecast` | `commodity`, optional `market`, `days` | Item list or `{ "items": [...] }` |

Weather fields use `temperature_c`, `rainfall_mm`, `rain_probability_pct`,
`humidity_pct`, `wind_speed_kph`, `wind_direction`, and a backend-provided
`advisory`. Forecast entries use the corresponding fields plus `date`,
`min_temperature_c`, and `max_temperature_c`. Scheme items use `name` (or
`title`), `scope`, `state`, `category`, `description`, `eligibility`,
`benefits`, `required_documents`, `application_deadline`, and `official_url`.
News items use `title`, `summary`, `source`, `published_at`, `category`, and
`original_url`. Market prices use `commodity`, `state`, `district`, `market`,
`min_price`, `modal_price`, `max_price`, `currency`, `unit`, and `price_date`;
history entries use `date`, `modal_price`, `currency`, and `unit`; forecast
entries use `date`, `predicted_modal_price`, `currency`, and `unit`.

Optional or missing backend fields are shown as unavailable. Price forecasts
are displayed as backend-provided estimates and are never calculated on the
device. Feature requests fail independently so an unavailable forecast does
not hide current market prices. Only HTTP(S) links are opened externally.

## Test

```shell
flutter analyze
flutter test
```
