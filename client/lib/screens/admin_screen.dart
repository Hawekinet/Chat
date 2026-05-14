import 'package:flutter/material.dart';

import '../services/api_service.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key, required this.api, required this.token});

  final ApiService api;
  final String token;

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  String role = 'user';
  String info = '';

  Future<void> createAccount() async {
    try {
      await widget.api.createUser(widget.token, usernameController.text, passwordController.text, role);
      setState(() => info = 'Пользователь создан');
    } catch (_) {
      setState(() => info = 'Ошибка создания');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Панель администратора', style: TextStyle(fontSize: 20)),
          TextField(controller: usernameController, decoration: const InputDecoration(labelText: 'Логин')),
          TextField(controller: passwordController, decoration: const InputDecoration(labelText: 'Пароль')),
          DropdownButton<String>(
            value: role,
            onChanged: (value) => setState(() => role = value ?? 'user'),
            items: const [
              DropdownMenuItem(value: 'user', child: Text('User')),
              DropdownMenuItem(value: 'admin', child: Text('Admin')),
            ],
          ),
          ElevatedButton(onPressed: createAccount, child: const Text('Создать учетную запись')),
          Text(info),
        ],
      ),
    );
  }
}
