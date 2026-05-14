import 'dart:io';

import 'package:dio/dio.dart';

class ApiService {
  ApiService({required this.baseUrl}) : dio = Dio(BaseOptions(baseUrl: baseUrl));

  final String baseUrl;
  final Dio dio;

  Future<(String, String)> login(String username, String password) async {
    final data = FormData.fromMap({'username': username, 'password': password});
    final response = await dio.post('/auth/token', data: data);
    return (response.data['access_token'] as String, response.data['role'] as String);
  }

  Future<List<dynamic>> fetchMessages(String token) async {
    final response = await dio.get('/messages',
        options: Options(headers: {'Authorization': 'Bearer $token'}));
    return response.data['items'] as List<dynamic>;
  }

  Future<void> sendMessage(String token, String text, {File? file, String mediaType = 'text'}) async {
    final formData = FormData.fromMap({
      'content': text,
      'media_type': mediaType,
      if (file != null) 'file': await MultipartFile.fromFile(file.path),
    });
    await dio.post('/messages',
        data: formData, options: Options(headers: {'Authorization': 'Bearer $token'}));
  }

  Future<void> createUser(String token, String username, String password, String role) async {
    final data = FormData.fromMap({'username': username, 'password': password, 'role': role});
    await dio.post('/admin/users',
        data: data, options: Options(headers: {'Authorization': 'Bearer $token'}));
  }
}
