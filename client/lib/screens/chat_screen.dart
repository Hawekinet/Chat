import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.api, required this.token});

  final ApiService api;
  final String token;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final textController = TextEditingController();
  List<dynamic> messages = [];

  @override
  void initState() {
    super.initState();
    loadMessages();
  }

  Future<void> loadMessages() async {
    final items = await widget.api.fetchMessages(widget.token);
    setState(() => messages = items);
  }

  Future<void> sendText() async {
    await widget.api.sendMessage(widget.token, textController.text);
    textController.clear();
    await loadMessages();
  }

  Future<void> sendFile() async {
    final result = await FilePicker.platform.pickFiles();
    if (result == null || result.files.single.path == null) return;
    final file = File(result.files.single.path!);
    final ext = result.files.single.extension?.toLowerCase() ?? '';
    final media = ['png', 'jpg', 'jpeg', 'gif'].contains(ext)
        ? 'image'
        : ['mp4', 'mov', 'avi'].contains(ext)
            ? 'video'
            : 'file';
    await widget.api.sendMessage(widget.token, 'Файл: ${result.files.single.name}', file: file, mediaType: media);
    await loadMessages();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: RefreshIndicator(
            onRefresh: loadMessages,
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index] as Map<String, dynamic>;
                return ListTile(
                  title: Text('${msg['sender_username']} • ${msg['media_type']}'),
                  subtitle: Text(msg['content'] ?? ''),
                );
              },
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(8),
          child: Row(
            children: [
              Expanded(child: TextField(controller: textController, decoration: const InputDecoration(hintText: 'Сообщение'))),
              IconButton(onPressed: sendFile, icon: const Icon(Icons.attach_file)),
              IconButton(onPressed: sendText, icon: const Icon(Icons.send)),
            ],
          ),
        )
      ],
    );
  }
}
