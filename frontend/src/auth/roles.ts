export type UserRole = "admin" | "manager" | "viewer";

export const USER_ROLES: UserRole[] = ["admin", "manager", "viewer"];

export const DEFAULT_ROLE: UserRole = "viewer";

export const ROLE_STORAGE_KEY = "detailWarehouseRole";

export function isUserRole(value: unknown): value is UserRole {
  return typeof value === "string" && USER_ROLES.includes(value as UserRole);
}

export function canCreate(role: UserRole): boolean {
  return role === "admin";
}

export function canEdit(role: UserRole): boolean {
  return role === "admin";
}

export function canDelete(role: UserRole): boolean {
  return role === "admin";
}

export function canUpdateQuantity(role: UserRole): boolean {
  return role === "admin" || role === "manager";
}
