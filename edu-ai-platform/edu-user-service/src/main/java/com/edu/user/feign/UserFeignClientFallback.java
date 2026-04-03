package com.edu.user.feign;

import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class UserFeignClientFallback implements UserFeignClient {
    
    @Override
    public Map<String, Object> getUserById(Long id) {
        return Map.of("error", "service unavailable");
    }
}
