package bb.back.quirkspring.socket;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {



    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        //registry.addHandler(new unex.cum.mdai.p1mdai.socket.MyWebSocketHandler(use, part), "/ws").setAllowedOrigins("*");
        registry.addHandler(new bb.back.quirkspring.socket.MyWebSocketHandler(), "/ws").setAllowedOrigins("*");
    }

}
