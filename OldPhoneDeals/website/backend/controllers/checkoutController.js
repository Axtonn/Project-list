const SalesLog = require("../models/SalesLog"); 
const Listing = require("../models/Listing");

// Route to handle checkout
exports.checkout = async (req, res) => {
  const { items, buyerName } = req.body; // This is an array of cart items

  // Calculate total
  const totalCost = items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);

  // Getting current time in UTC+10
  const now = new Date();
  const timezoneOffsetMs = now.getTimezoneOffset() * 60 * 1000;
  const localDateAsUTC = new Date(now.getTime() - timezoneOffsetMs);

  const saleDocument = {
    items: items,
    totalCost: totalCost,
    soldAt: localDateAsUTC,
    buyerName: buyerName || "Unknown"
  };

  try {
    // Updating the stock for each item
    for (const item of items) {
      const dbItem = await Listing.findById(item._id);

      if (!dbItem) {
        return res.status(404).json({ error: `Item not found: ${item.item}` });
      }

      // Check if enough stock is available
      if (dbItem.stock < item.quantity) {
        return res.status(400).json({ error: `Not enough stock for item: ${item.item}` });
      }

      dbItem.stock -= item.quantity;
      await dbItem.save(); // Save the updated stock
    }

    // Logging the sale
    const salesLog = await SalesLog.create(saleDocument);
    res.status(201).json({ message: 'Sales logged successfully', salesLog });
  } catch (err) {
    console.error('Error logging sale:', err);
    res.status(500).json({ error: 'Failed to log sale' });
  }
}

// Route to export sales logs in JSON format
exports.exportSales = async (req, res) => {
  try {
    // Fetch all sales logs from the database
    const salesLogs = await SalesLog.find();

    // Send the sales logs as JSON
    res.header('Content-Type', 'application/json');
    res.attachment('sales_export.json');
    return res.send(JSON.stringify(salesLogs, null, 2)); // Format with indentation for readability
  } catch (err) {
    console.error('Error exporting sales:', err);
    res.status(500).json({ error: 'Failed to export sales' });
  }
}