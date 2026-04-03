package com.edu.user.service;

import com.edu.user.entity.User;
import com.edu.user.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    public User findByUsername(String username) {
        return userMapper.selectOne(
            new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<User>()
                .eq("username", username)
        );
    }
    
    public User findById(Long id) {
        return userMapper.selectById(id);
    }
    
    public void save(User user) {
        userMapper.insert(user);
    }
}
