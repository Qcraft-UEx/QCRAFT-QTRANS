package bb.back.quirkspring.util;

import java.security.SecureRandom;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

public class CodeGenerator {
    private static final String CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    private static final int CODE_LENGTH = 5;
    private static final Random RANDOM = new SecureRandom();
    private static final Set<String> USED_CODES = new HashSet<>();

    /**
     * Genera un código único de 5 caracteres alfanuméricos (A–Z, 0–9).
     * @return un código único
     * @throws IllegalStateException si se agotan las combinaciones posibles
     */
    public static synchronized String generateCode() {
        // Número total de combinaciones posibles: 36^5 = 60.466.176
        if (USED_CODES.size() >= Math.pow(CHARACTERS.length(), CODE_LENGTH)) {
            throw new IllegalStateException("Se han agotado todas las combinaciones posibles.");
        }

        String code;
        do {
            StringBuilder sb = new StringBuilder(CODE_LENGTH);
            for (int i = 0; i < CODE_LENGTH; i++) {
                int idx = RANDOM.nextInt(CHARACTERS.length());
                sb.append(CHARACTERS.charAt(idx));
            }
            code = sb.toString();
        } while (USED_CODES.contains(code));

        USED_CODES.add(code);
        return code;
    }

}
