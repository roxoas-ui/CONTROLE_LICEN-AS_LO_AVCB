<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Conditional extends Model
{
    use HasFactory;

    protected $fillable = [
        'license_id',
        'description',
        'due_date',
        'frequency',
        'status',
    ];

    protected $casts = [
        'due_date' => 'date',
    ];

    public function license()
    {
        return $this->belongsTo(License::class);
    }

    public function executions()
    {
        return $this->hasMany(ConditionalExecution::class);
    }
}
