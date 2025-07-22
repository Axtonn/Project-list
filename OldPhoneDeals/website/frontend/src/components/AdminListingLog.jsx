import { useEffect, useState } from 'react';
import axios from 'axios';

const AdminListingLog = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:3000/api/admin/listing-log/logs', { withCredentials: true })
        .then(res => {
        // console.log(res.data);
        setLogs(res.data);
        })
        .catch(err => {
        console.error('Failed to fetch listing logs:', err);
        alert('Could not load logs.');
        });
    }, []);


  return (
    <div style={{ padding: '1rem' }} className='listing-container'>
      <h3>Listing Input Logs</h3>
      {logs.length === 0 ? (
        <p>No logs found.</p>
      ) : (
       <table className="log-table">
            <thead>
                <tr>
                <th>No.</th>
                <th>User</th>
                <th>Listing ID</th>
                <th>Title</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Action</th>
                <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {[...logs].reverse().map((log, index) => (
                <tr key={log._id}>
                    <td>{index + 1}</td>
                    <td>{log.user?.firstname} {log.user?.lastname}</td>
                    <td>{log.listingId || 'N/A'}</td>
                    <td>{log.title}</td>
                    <td>${log.price}</td>
                    <td>{log.stock}</td>
                    <td>{log.action}</td>
                    <td>{new Date(log.createdAt).toLocaleString()}</td>
                </tr>
                ))}
            </tbody>
        </table>


      )}
    </div>
  );
};

export default AdminListingLog;
