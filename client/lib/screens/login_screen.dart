import 'package:flutter/material.dart';

import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.onLogin, required this.api});

  final ApiService api;
  final void Function(String token, String role) onLogin;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  String? error;

  Future<void> login() async {
    try {
      final result = await widget.api.login(usernameController.text, passwordController.text);
      widget.onLogin(result.$1, result.$2);
    } catch (_) {
      setState(() => error = 'Ошибка авторизации');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SizedBox(
          width: 360,
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Вход во внутренний чат', style: TextStyle(fontSize: 20)),
                  TextField(controller: usernameController, decoration: const InputDecoration(labelText: 'Логин')),
                  TextField(controller: passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Пароль')),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: login, child: const Text('Войти')),
                  if (error != null) Text(error!, style: const TextStyle(color: Colors.red))
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
