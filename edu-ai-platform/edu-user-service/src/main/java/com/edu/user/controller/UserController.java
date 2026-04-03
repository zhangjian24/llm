package com.edu.user.controller;

import com.edu.user.dto.LoginRequest;
import com.edu.user.dto.RegisterRequest;
import com.edu.user.entity.User;
import com.edu.user.security.JwtUtil;
import com.edu.user.service.UserService;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Autowired
    private BCryptPasswordEncoder passwordEncoder;
    
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        User user = userService.findByUsername(request.getUsername());
        
        if (user == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "用户名或密码错误"));
        }
        
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return ResponseEntity.badRequest().body(Map.of("message", "用户名或密码错误"));
        }
        
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        
        Map<String, Object> result = new HashMap<>();
        result.put("token", token);
        result.put("userInfo", Map.of(
            "id", user.getId(),
            "username", user.getUsername(),
            "nickname", user.getNickname(),
            "email", user.getEmail()
        ));
        
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        User existUser = userService.findByUsername(request.getUsername());
        if (existUser != null) {
            return ResponseEntity.badRequest().body(Map.of("message", "用户名已存在"));
        }
        
        User newUser = new User();
        newUser.setUsername(request.getUsername());
        newUser.setPassword(passwordEncoder.encode(request.getPassword()));
        newUser.setEmail(request.getEmail());
        newUser.setNickname(request.getUsername());
        newUser.setStatus(1);
        newUser.setCreateTime(LocalDateTime.now());
        newUser.setUpdateTime(LocalDateTime.now());
        
        userService.save(newUser);
        
        return ResponseEntity.ok(Map.of("message", "注册成功"));
    }
    
    @GetMapping("/info")
    public ResponseEntity<?> getUserInfo(@RequestHeader("Authorization") String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(401).body(Map.of("message", "未授权"));
        }
        
        String token = authHeader.substring(7);
        if (!jwtUtil.validateToken(token)) {
            return ResponseEntity.status(401).body(Map.of("message", "Token无效"));
        }
        
        Long userId = jwtUtil.getUserIdFromToken(token);
        User user = userService.findById(userId);
        
        if (user == null) {
            return ResponseEntity.status(404).body(Map.of("message", "用户不存在"));
        }
        
        return ResponseEntity.ok(Map.of(
            "id", user.getId(),
            "username", user.getUsername(),
            "nickname", user.getNickname(),
            "email", user.getEmail()
        ));
    }
}
