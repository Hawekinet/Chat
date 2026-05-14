import 'package:flutter/material.dart';

import 'screens/admin_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/login_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(const LanChatApp());
}

class LanChatApp extends StatefulWidget {
  const LanChatApp({super.key});

  @override
  State<LanChatApp> createState() => _LanChatAppState();
}

class _LanChatAppState extends State<LanChatApp> {
  final api = ApiService(baseUrl: 'http://192.168.1.10:8000');
  String? token;
  String role = 'user';

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LAN Chat',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: token == null
          ? LoginScreen(
              onLogin: (newToken, newRole) {
                setState(() {
                  token = newToken;
                  role = newRole;
                });
              },
              api: api,
            )
          : DefaultTabController(
              length: role == 'admin' ? 2 : 1,
              child: Scaffold(
                appBar: AppBar(
                  title: const Text('Internal LAN Chat'),
                  bottom: TabBar(
                    tabs: [
                      const Tab(text: 'Chat'),
                      if (role == 'admin') const Tab(text: 'Admin')
                    ],
                  ),
                  actions: [
                    IconButton(
                      onPressed: () => setState(() => token = null),
                      icon: const Icon(Icons.logout),
                    )
                  ],
                ),
                body: TabBarView(
                  children: [
                    ChatScreen(api: api, token: token!),
                    if (role == 'admin') AdminScreen(api: api, token: token!),
                  ],
                ),
              ),
            ),
    );
  }
}
