from jobs.models import JobPost


class UserComponent:
    def can_delete(self):
        return False

    def delete_job(self, job_id):
        raise PermissionError("This user has cannot delete jobs.")


class NormalUserComponent(UserComponent):
    def __init__(self, django_user):
        self.user = django_user

    def delete_job(self, job_id):
        try:
            job = JobPost.objects.get(id=job_id)
        except JobPost.DoesNotExist:
            return False, "Job not found."

        job.delete()
        return True, "Job deleted successfully."


class UserDecoratorBase(UserComponent):
    def __init__(self, wrapped_user: UserComponent):
        self._wrapped_user = wrapped_user

    def can_delete(self):
        return self._wrapped_user.can_delete()

    def delete_job(self, job_id):
        return self._wrapped_user.delete_job(job_id)


class AdminUserDecorator(UserDecoratorBase):
    def can_delete(self):
        return True

    def delete_job(self, job_id):
        try:
            job = JobPost.objects.get(id=job_id)
            job.delete()
            return True, "Job deleted successfully."
        except JobPost.DoesNotExist:
            return False, "Job not found."
