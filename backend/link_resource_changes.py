from database import get_connection


def link_resource_changes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE infrastructure_changes ic
        SET resource_id = ir.id
        FROM infrastructure_resources ir
        WHERE ic.terraform_resource_name =
              ir.resource_type || '.' || ir.resource_name
          AND ic.file_path = ir.file_path;
    """)

    connection.commit()

    print(
        f"Linked {cursor.rowcount} infrastructure changes "
        f"to Terraform resources."
    )

    cursor.close()
    connection.close()


if __name__ == "__main__":
    link_resource_changes()