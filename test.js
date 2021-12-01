$.ajax({
    url: "{% url 'add_lesson' day_id=day.id %}",
    data: {
        'subject': subjectInput,
        'description': descriptionInput,
        'homework': homeworkInput,
        'grade': gradeInput
    },
    dataType: 'json',
    success: function (data) {
        if (data.lesson) {
          appendToUsrTable(data.lesson);
        }
    }
});