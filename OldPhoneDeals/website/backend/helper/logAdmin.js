const AdminLog = require('../models/AdminLog');

async function logAdminAction({ adminname, action, subject, subject_identifier }) {
  try {
    const logEntry = new AdminLog({
      adminname,
      action,
      subject,
      subject_identifier
    });

    await logEntry.save();
    // console.log('Admin action logged:', logEntry);
  } catch (err) {
    console.error('Failed to log admin action:', err.message);
  }
}

module.exports = logAdminAction;