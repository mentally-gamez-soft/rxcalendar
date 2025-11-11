# Quick Reference: User Permissions

## Flag Access by Role

### 🟦 HR Services (Full Access)
✅ All flags available:
- national day off
- Akkodis offered day off  
- regional day off
- offered vacation client closed
- on vacation client closed
- extra day off
- on vacation
- (blank)

**HR Users:**
- Michael Scott (hr001)
- Nancy Drew (hr002)
- Oscar Wilde (hr003)
- Patricia Hill (hr004)
- Quincy Adams (hr005)

---

### 🔵 Managers (Extended Access)
✅ Can set:
- offered vacation client closed
- on vacation client closed
- extra day off
- on vacation
- (blank)

❌ Cannot set:
- national day off
- Akkodis offered day off
- regional day off

**Manager Users:**
- Kevin Anderson (mgr001)
- Laura Martinez (mgr002)

---

### ⚪ Employees (Limited Access)
✅ Can only set:
- extra day off
- on vacation
- (blank)

❌ Cannot set:
- offered vacation client closed
- on vacation client closed
- national day off
- Akkodis offered day off
- regional day off

**Employee Users:**
- Alice Johnson (emp001)
- Bob Smith (emp002)
- Charlie Brown (emp003)
- Diana Prince (emp004)
- Ethan Hunt (emp005)
- Fiona Green (emp006)
- George Wilson (emp007)
- Hannah White (emp008)
- Ian Malcolm (emp009)
- Julia Roberts (emp010)

---

## How to Use

1. **Switch User**: Click "Switch User" button in the header
2. **Select Role**: Choose from Employees, Managers, or HR Services
3. **Add Comment**: Click on a weekday date
4. **Select Flag**: Only permitted flags will be available in the dropdown
5. **Save**: System validates your permission before saving

## Access Denied?

If you try to save a flag you don't have permission for, you'll see:
> ⚠️ **Access Denied**: [Your Role] cannot set '[flag name]' flag

**Solution**: Switch to a user with appropriate permissions or select a different flag.

---

## Feature Highlights

- 🔐 **Role-based permissions** prevent unauthorized flag assignments
- 📝 **Audit trail** records who made each change
- 👥 **User switching** simulates different roles (for demo purposes)
- ✅ **Dynamic UI** only shows flags you can access
- 🚫 **Validation** on both frontend (UI) and backend (save logic)
