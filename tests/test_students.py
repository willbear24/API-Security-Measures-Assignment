class TestCreateStudent:
    """Tests for POST /students"""

    def test_create_student_success(self, client, auth_headers):
        response = client.post(
            "/students",
            headers=auth_headers,
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "grade_level": 10,
                "gpa": 3.8,
                "is_enrolled": True,
            },
        )

        assert response.status_code == 201

    def test_create_student_missing_name(self, client, auth_headers):
        response = client.post(
            "/students",
            headers=auth_headers,
            json={"email": "jane@example.com", "grade_level": 10},
        )
        assert response.status_code == 422

    def test_create_student_invalid_grade_level(self, client, auth_headers):
        response = client.post(
            "/students",
            headers=auth_headers,
            json={"name": "Jane Doe", "email": "jane@example.com", "grade_level": 13},
        )
        assert response.status_code == 422

    def test_create_student_empty_name(self, client, auth_headers):
        response = client.post(
            "/students",
            headers=auth_headers,
            json={"name": "", "email": "jane@example.com", "grade_level": 10},
        )
        assert response.status_code == 422

    def test_create_student_requires_authentication(self, client):
        response = client.post(
            "/students",
            json={"name": "Jane Doe", "email": "jane@example.com", "grade_level": 10},
        )

        assert response.status_code == 401

    def test_create_student_strips_script_tags_from_name(self, client, auth_headers):
        response = client.post(
            "/students",
            headers=auth_headers,
            json={
                "name": "<script>alert('xss')</script>Jane Doe",
                "email": "jane.sanitized@example.com",
                "grade_level": 10,
            },
        )

        assert response.status_code == 201
        name = response.json()["name"]
        assert "<script>" not in name
        assert "</script>" not in name
        assert name == "alert('xss')Jane Doe"


class TestReadStudents:
    """Tests for GET /students and GET /students/{id}"""

    def test_list_students_empty(self, client):
        response = client.get("/students")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_students_with_data(self, client, sample_student):
        response = client.get("/students", params={"grade_level": 12})
        assert response.status_code == 200
        students = response.json()
        assert any(student["id"] == sample_student["id"] for student in students)

    def test_get_student_by_id(self, client, sample_student):
        response = client.get(f"/students/{sample_student['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Name"

    def test_get_student_not_found(self, client):
        response = client.get("/students/9999")
        assert response.status_code == 404


class TestUpdateStudent:
    """Tests for PATCH /students/{id}"""

    def test_patch_student_name(self, client, sample_student, auth_headers):
        response = client.patch(
            f"/students/{sample_student['id']}",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["email"] == "test@email.com"  # Unchanged

    def test_patch_nonexistent_student(self, client, auth_headers):
        response = client.patch(
            "/students/9999", headers=auth_headers, json={"name": "Nope"}
        )
        assert response.status_code == 404


class TestDeleteStudent:
    """Tests for DELETE /students/{id}"""

    def test_delete_student(self, client, sample_student, auth_headers):
        response = client.delete(
            f"/students/{sample_student['id']}", headers=auth_headers
        )
        assert response.status_code == 204
        # Verify it's gone
        response = client.get(f"/students/{sample_student['id']}")
        assert response.status_code == 404

    def test_delete_nonexistent_student(self, client, auth_headers):
        response = client.delete("/students/9999", headers=auth_headers)
        assert response.status_code == 404
