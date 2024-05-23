import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class App{

    // JDBC URL, username, and password of MySQL server
    private static final String URL = "jdbc:mysql://localhost:3306/cafeteria";
    private static final String USER = "root";
    private static final String PASSWORD = "Harshitha@555";

    public static void main(String[] args) {
        Connection connection = null;
        PreparedStatement preparedStatement = null;

        try {
            // Load MySQL JDBC Driver
            Class.forName("com.mysql.cj.jdbc.Driver");
            System.out.println("MySQL JDBC Driver Registered!");

            // Establish the connection
            connection = DriverManager.getConnection(URL, USER, PASSWORD);
            System.out.println("Connection established!");

            // SQL INSERT statement
            String insertSQL = "INSERT INTO Users (name, role, password) VALUES (?, ?, ?)";

            // Create a PreparedStatement
            preparedStatement = connection.prepareStatement(insertSQL);

            // Insert first user
            preparedStatement.setString(1, "Jane Smith");
            preparedStatement.setString(2, "Chef");
            preparedStatement.setString(3, "chefpass456");
            preparedStatement.addBatch();

            // Insert second user
            preparedStatement.setString(1, "Emily Johnson");
            preparedStatement.setString(2, "Employee");
            preparedStatement.setString(3, "employeepass789");
            preparedStatement.addBatch();

            // Insert third user
            preparedStatement.setString(1, "Michael Brown");
            preparedStatement.setString(2, "Admin");
            preparedStatement.setString(3, "adminpass321");
            preparedStatement.addBatch();

            // Execute batch insert
            int[] rowsInserted = preparedStatement.executeBatch();
            System.out.println(rowsInserted.length + " users inserted successfully!");

        } catch (ClassNotFoundException e) {
            System.out.println("Where is your MySQL JDBC Driver?");
            e.printStackTrace();
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            // Close resources
            try {
                if (preparedStatement != null) preparedStatement.close();
                if (connection != null) connection.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
