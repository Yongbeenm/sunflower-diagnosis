import { z } from "zod";

export const loginSchema = z.object({
  identifier: z.string().min(1, { message: "auth.validation.identifier_required" }),
  password: z.string().min(1, { message: "auth.validation.password_required" }),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  email: z.string().email({ message: "auth.validation.email_invalid" }),
  username: z
    .string()
    .min(3, { message: "auth.validation.username_min" })
    .max(64, { message: "auth.validation.username_max" })
    .regex(/^[a-zA-Z0-9_-]+$/, { message: "auth.validation.username_pattern" }),
  password: z
    .string()
    .min(8, { message: "auth.validation.password_min" })
    .max(128, { message: "auth.validation.password_max" }),
});

export type RegisterFormData = z.infer<typeof registerSchema>;
