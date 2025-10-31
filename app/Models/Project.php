<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Project extends Model
{
    use HasFactory;

    protected $fillable = [
        'client_id',
        'name',
        'description',
        'location',
    ];

    protected $casts = [
        'location' => 'array',
    ];

    public function client()
    {
        return $this->belongsTo(Client::class);
    }

    public function licenses()
    {
        return $this->hasMany(License::class);
    }

    public function avcbs()
    {
        return $this->hasMany(Avcb::class);
    }
}
