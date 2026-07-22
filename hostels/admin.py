from django.contrib import admin

from .models import Hostel, HostelExpense, Room, RoomAllocation, VisitorLog


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'warden', 'capacity', 'occupancy', 'available_spaces', 'is_active')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'school__name', 'warden__username')
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hostel', 'floor', 'capacity', 'occupancy', 'available_spaces', 'is_active')
    list_filter = ('hostel__school', 'hostel', 'is_active')
    search_fields = ('room_number', 'hostel__name')


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'session', 'allocated_at', 'released_at', 'is_active')
    list_filter = ('room__hostel__school', 'room__hostel', 'session', 'is_active')
    search_fields = ('student__username', 'room__room_number', 'room__hostel__name')
    readonly_fields = ('allocated_at',)


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'hostel', 'student', 'visitor_phone', 'checked_in_at', 'checked_out_at')
    list_filter = ('hostel__school', 'hostel', 'checked_in_at')
    search_fields = ('visitor_name', 'visitor_phone', 'purpose', 'student__username')


@admin.register(HostelExpense)
class HostelExpenseAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'category', 'amount', 'expense_date', 'recorded_by')
    list_filter = ('hostel__school', 'hostel', 'category', 'expense_date')
    search_fields = ('category', 'description', 'hostel__name')
