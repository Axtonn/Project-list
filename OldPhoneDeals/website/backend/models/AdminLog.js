const mongoose = require('mongoose');

const adminLogSchema = new mongoose.Schema({
  adminname: {
    type: String, required: true
  },
  action: {
    type: String, required: true
  },
  subject: {
    type: String, required: true
  },
  subject_identifier : {
    type: String, required: true
  },
  time: { 
    type: Date, default: Date.now 
  },
});

module.exports = mongoose.model('AdminLog', adminLogSchema);