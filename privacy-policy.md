# Privacy Policy — Vion - Smart IPTV Player

**Effective date:** 16 October 2026
**App:** Vion - Smart IPTV Player (`com.vion.iptv`)
**Contact:** weazovion@gmail.com

[العربية في الأسفل](#سياسة-الخصوصية--فيون)

---

## 1. Summary

Vion is a media player. It does not provide, host or sell any TV channels or video content. You add your own playlists.

- An account is **optional**. You can use the whole app as a guest without giving us any personal data.
- If you create an account, we store your name, email, country and a backup of your lists so you can restore them on a new phone.
- The app uses **Google Firebase** (accounts, backup, anonymous crash reports and usage statistics) and shows ads through **Google AdMob**.
- You can delete your account and its data at any time: <https://weazo.github.io/vion-iptv-data/delete-account/>

## 2. Data stored on your device

The following is saved locally on your device:

- Playlists and sources you add: M3U links, Xtream Codes server, username and password, Stalker portal address and MAC, local files.
- Favourites, your own lists, watch history and "continue watching".
- Channels you report (pornography, gambling, violence…). Reports are **local only** and are not uploaded; they just hide the channel on your device.
- App settings: language, theme, countries and languages you chose, playback preferences.
- Technical playback statistics used to pick the best player for a stream. These are stored under a one-way hash of the stream address, not the address itself.
- Short-lived picture snapshots of channels, kept in memory for up to 15 minutes.

Without an account, none of this leaves your device. You can delete it at any time by clearing the app's data or uninstalling the app.

## 3. Your account (optional)

You can create an account with **Google sign-in** or with **email and password**. Sign-in is handled by Google Firebase Authentication; we never see your Google password.

If you create an account, we store in Google Firebase (Cloud Firestore, servers in the European Union):

- **Account details:** your name, email address, country, sign-in method and an account ID.
- **Device details:** device model, app version, app language, account creation and last sign-in dates, and the number of favourites and sources.
- **Backup of your lists:** your sources (including playlist links and, for Xtream Codes / Stalker sources, the username, password or MAC you entered), your favourite lists, and the countries and languages you chose for Home.

**Why:** to let you sign in on another phone and get your lists back, and to understand how many people use the app in each country.

The backup is updated when the app goes to the background. Only you (signed in to your account) can read or change your data; the database rules block access by anyone else. Data is sent over encrypted connections (HTTPS).

We do **not** sell your personal data and we do **not** use your name or email for advertising.

## 4. Crash reports and usage statistics (Firebase)

To find and fix problems, the app uses **Firebase Crashlytics** and **Google Analytics for Firebase**. They may collect:

- Crash logs and diagnostic information (device model, Android version, app version, the state of the app when it crashed)
- Installation identifiers and anonymous app usage events

This data is used only to keep the app stable and to improve it. Crashlytics data is kept for up to 90 days. Learn more: <https://firebase.google.com/support/privacy>.

## 5. Network connections the app makes

To work, the app connects to:

- **The servers in the playlists you add** (your IPTV provider) to load channel lists and play streams. Those servers receive your IP address and the requests needed for playback. Their privacy practices are set by your provider, not by us.
- **The built-in Vion channel list**, hosted on GitHub Pages (`weazo.github.io`), and, if you enable it, the public **iptv-org** list (`iptv-org.github.io`). These are plain file downloads. GitHub may log IP addresses as described in GitHub's privacy statement.
- **Channel logo addresses** included in playlists, to show channel images.
- **Google Firebase** for accounts, backup, crash reports and statistics (see above).
- **Google Play services** for in-app updates, sign-in, casting and ads.
- **TVs on your local Wi-Fi**, only when you open the cast menu: the app looks for Chromecast / Google TV and DLNA devices on your network and sends the stream address of the channel you choose to the TV. Nothing is sent outside your network for this.

## 6. Advertising (Google AdMob)

The app shows banner, full-screen and optional rewarded video ads provided by Google AdMob. AdMob may collect and process:

- Device identifiers, including the **Android Advertising ID**
- IP address and approximate location derived from it
- App interactions with ads (views, clicks) and diagnostic information related to ads

Google uses this data to show, measure and improve ads and to prevent fraud. Learn more: <https://policies.google.com/technologies/partner-sites>.

You can reset your Advertising ID or opt out of personalised ads in your device settings (**Settings → Google → Ads** or **Settings → Privacy → Ads**). Ads are not shown on Android TV.

## 7. Permissions

| Permission | Why |
|---|---|
| Internet, network state | Load playlists, play streams, sign in and back up |
| Wi-Fi multicast | Find TVs on your local network for casting |
| Notifications | Show playback controls while a channel plays in the background |
| Foreground service (media playback), wake lock | Keep playing when the app is in the background or the screen is off |
| Advertising ID / ad services | Used by Google AdMob for ads |

The app does not access your contacts, camera, microphone, photos or precise location.

## 8. Children

The app is not directed to children under 13 (or the minimum age in your country) and we do not knowingly collect data from children.

## 9. Content responsibility

Vion only plays what you add. Please add only playlists you have the right to watch. We have no control over third-party streams.

## 10. Your rights and deleting your data

- **Guest users:** all data stays on your device. Clear the app's data or uninstall the app to remove it.
- **Account users:** you can view and change your data in the app, sign out at any time, and delete your account from **Settings → Account → Delete account**. This deletes your account and cloud backup immediately.
- **Without the app:** follow the steps at <https://weazo.github.io/vion-iptv-data/delete-account/> or email **weazovion@gmail.com** from the address you signed up with. We delete the account within 30 days.

Depending on where you live (for example under the GDPR in the EU), you may also have the right to access, correct or export your data, or to object to its processing. Email us and we will reply within 30 days.

For data collected by Google (AdMob, Firebase), see Google's privacy policy: <https://policies.google.com/privacy>.

## 11. Changes

We may update this policy. Changes are posted on this page with a new effective date.

## 12. Contact

Questions about this policy: **weazovion@gmail.com**

---

# سياسة الخصوصية — فيون

**تاريخ السريان:** 16 أكتوبر 2026
**التطبيق:** Vion - Smart IPTV Player (`com.vion.iptv`)
**للتواصل:** weazovion@gmail.com

## 1. ملخص

فيون مشغل وسائط. لا يوفر ولا يستضيف ولا يبيع أي قنوات أو محتوى مرئي، وأنت من يضيف قوائم التشغيل.

- الحساب **اختياري**، ويمكنك استخدام التطبيق كاملاً كضيف دون إعطائنا أي بيانات شخصية.
- إذا أنشأت حساباً، نحفظ اسمك وبريدك ودولتك ونسخة احتياطية من قوائمك لتستعيدها على هاتف جديد.
- يستخدم التطبيق **Google Firebase** للحسابات والنسخ الاحتياطي وتقارير الأعطال المجهولة وإحصائيات الاستخدام، ويعرض إعلانات من **Google AdMob**.
- يمكنك حذف حسابك وبياناته في أي وقت: <https://weazo.github.io/vion-iptv-data/delete-account/>

## 2. البيانات المحفوظة على جهازك

يُحفظ ما يلي على جهازك:

- القوائم والمصادر التي تضيفها: روابط M3U، وخادم Xtream Codes مع اسم المستخدم وكلمة المرور، وعنوان بوابة Stalker وMAC، والملفات المحلية.
- المفضلة وقوائمك الخاصة وسجل المشاهدة و"متابعة المشاهدة".
- القنوات التي تبلّغ عنها. البلاغات **محلية فقط** ولا تُرفع إلى أي خادم، ووظيفتها إخفاء القناة على جهازك.
- إعدادات التطبيق: اللغة والمظهر والدول واللغات التي اخترتها وتفضيلات التشغيل.
- إحصائيات تقنية تساعد في اختيار أفضل مشغل لكل بث. تُحفظ ببصمة مشفّرة باتجاه واحد للرابط، لا بالرابط نفسه.
- لقطات مؤقتة من القنوات، تبقى في الذاكرة 15 دقيقة كحد أقصى.

بدون حساب، لا يخرج أي شيء من هذا من جهازك. يمكنك حذفه في أي وقت بمسح بيانات التطبيق أو حذفه.

## 3. حسابك (اختياري)

يمكنك إنشاء حساب عن طريق **تسجيل الدخول بحساب Google** أو عن طريق **البريد الإلكتروني وكلمة المرور**. تتولى خدمة Google Firebase Authentication عملية الدخول، ولا نرى كلمة مرور Google الخاصة بك أبداً.

إذا أنشأت حساباً، نحفظ في Google Firebase (قاعدة Cloud Firestore، وخوادمها في الاتحاد الأوروبي):

- **بيانات الحساب:** اسمك وبريدك الإلكتروني ودولتك وطريقة الدخول ومعرّف الحساب.
- **بيانات الجهاز:** نوع الجهاز وإصدار التطبيق ولغته، وتاريخ إنشاء الحساب وآخر دخول، وعدد المفضلة والمصادر.
- **النسخة الاحتياطية لقوائمك:** مصادرك (ومنها روابط القوائم، وكذلك اسم المستخدم وكلمة المرور أو MAC الذي أدخلته لمصادر Xtream Codes وStalker)، وقوائم المفضلة، والدول واللغات التي اخترتها للشاشة الرئيسية.

**السبب:** لتستطيع الدخول من هاتف آخر واستعادة قوائمك، ولنعرف عدد مستخدمي التطبيق في كل دولة.

تُحدَّث النسخة الاحتياطية عند خروجك من التطبيق إلى الخلفية. لا يستطيع قراءة بياناتك أو تعديلها إلا أنت وأنت مسجّل الدخول في حسابك، وقواعد قاعدة البيانات تمنع وصول أي شخص آخر إليها. تُرسل البيانات عبر اتصال مشفّر (HTTPS).

**لا** نبيع بياناتك الشخصية، و**لا** نستخدم اسمك أو بريدك للإعلانات.

## 4. تقارير الأعطال وإحصائيات الاستخدام (Firebase)

لاكتشاف المشاكل وإصلاحها، يستخدم التطبيق **Firebase Crashlytics** و**Google Analytics for Firebase**. قد تجمع هاتان الخدمتان:

- سجلات الأعطال ومعلومات تشخيصية: نوع الجهاز وإصدار Android وإصدار التطبيق، وحالة التطبيق لحظة العطل.
- معرّفات التثبيت، وأحداث استخدام مجهولة الهوية.

تُستخدم هذه البيانات فقط للحفاظ على استقرار التطبيق وتحسينه. تبقى بيانات Crashlytics مدة أقصاها 90 يوماً. للمزيد: <https://firebase.google.com/support/privacy>

## 5. الاتصالات التي يجريها التطبيق

ليعمل التطبيق، يتصل بما يلي:

- **خوادم القوائم التي تضيفها** (مزوّد IPTV الخاص بك) لتحميل القنوات وتشغيلها. هذه الخوادم ترى عنوان IP الخاص بك وطلبات التشغيل، وتخضع لسياسة مزوّدك لا لسياستنا.
- **قائمة فيون المدمجة**، المستضافة على GitHub Pages (`weazo.github.io`)، وقائمة **iptv-org** العامة (`iptv-org.github.io`) إذا فعّلتها. هي تحميل ملفات فقط، وقد يسجّل GitHub عناوين IP وفق سياسة خصوصيته.
- **روابط شعارات القنوات** الموجودة في القوائم، لعرض صورها.
- **Google Firebase** للحسابات والنسخ الاحتياطي وتقارير الأعطال والإحصائيات (انظر أعلاه).
- **خدمات Google Play** للتحديث داخل التطبيق وتسجيل الدخول والبث إلى التلفزيون والإعلانات.
- **أجهزة التلفزيون على شبكة Wi-Fi المنزلية**، وذلك فقط عند فتح قائمة البث إلى التلفزيون: يبحث التطبيق عن أجهزة Chromecast / Google TV وDLNA في شبكتك، ثم يرسل رابط القناة التي تختارها إلى التلفزيون. لا يُرسل شيء من هذا خارج شبكتك.

## 6. الإعلانات (Google AdMob)

يعرض التطبيق إعلانات بانر وإعلانات بملء الشاشة وفيديو بمكافأة اختياري من Google AdMob. قد يجمع AdMob:

- معرّفات الجهاز، ومنها **معرّف الإعلانات في Android**
- عنوان IP والموقع التقريبي المستنتج منه
- تفاعلك مع الإعلانات (المشاهدات والنقرات) وبيانات تشخيصية متعلقة بالإعلانات

تستخدم Google هذه البيانات لعرض الإعلانات وقياسها وتحسينها ومنع الاحتيال. للمزيد: <https://policies.google.com/technologies/partner-sites>

يمكنك إعادة تعيين معرّف الإعلانات أو إيقاف الإعلانات المخصصة من إعدادات جهازك (**الإعدادات ← Google ← الإعلانات**). لا تظهر إعلانات على Android TV.

## 7. الصلاحيات

| الصلاحية | السبب |
|---|---|
| الإنترنت وحالة الشبكة | تحميل القوائم وتشغيل البث وتسجيل الدخول والنسخ الاحتياطي |
| Wi-Fi multicast | البحث عن أجهزة التلفزيون في شبكتك للبث إليها |
| الإشعارات | عرض أزرار التحكم أثناء التشغيل في الخلفية |
| خدمة في المقدمة (تشغيل وسائط) وإبقاء الجهاز نشطاً | متابعة التشغيل والتطبيق في الخلفية أو الشاشة مطفأة |
| معرّف الإعلانات / خدمات الإعلانات | يستخدمها Google AdMob للإعلانات |

لا يصل التطبيق إلى جهات الاتصال أو الكاميرا أو الميكروفون أو الصور أو موقعك الدقيق.

## 8. الأطفال

التطبيق غير موجّه للأطفال دون 13 عاماً (أو السن الأدنى في بلدك)، ولا نجمع بيانات الأطفال عن علم.

## 9. المسؤولية عن المحتوى

فيون يشغّل فقط ما تضيفه أنت. أضف فقط القوائم التي يحق لك مشاهدتها. ليس لدينا أي تحكم في البث من أطراف ثالثة.

## 10. حقوقك وحذف بياناتك

- **إذا كنت ضيفاً:** كل بياناتك تبقى على جهازك، ويمكنك حذفها بمسح بيانات التطبيق أو إزالته.
- **إذا كان لديك حساب:** يمكنك عرض بياناتك وتعديلها من داخل التطبيق، وتسجيل الخروج في أي وقت، وحذف حسابك من **الإعدادات ← الحساب ← حذف الحساب**. يحذف ذلك حسابك ونسختك الاحتياطية فوراً.
- **بدون التطبيق:** اتبع الخطوات في <https://weazo.github.io/vion-iptv-data/delete-account/> أو أرسل بريداً إلى **weazovion@gmail.com** من نفس العنوان الذي سجّلت به. نحذف الحساب خلال 30 يوماً.

حسب مكان إقامتك (مثل اللائحة الأوروبية العامة لحماية البيانات GDPR)، قد يكون لك أيضاً الحق في الاطلاع على بياناتك أو تصحيحها أو تصديرها أو الاعتراض على معالجتها. راسلنا وسنرد خلال 30 يوماً.

للبيانات التي تجمعها Google (AdMob وFirebase)، راجع سياسة خصوصية Google: <https://policies.google.com/privacy>

## 11. التغييرات

قد نحدّث هذه السياسة. تُنشر التغييرات في هذه الصفحة مع تاريخ سريان جديد.

## 12. التواصل

للأسئلة حول هذه السياسة: **weazovion@gmail.com**
